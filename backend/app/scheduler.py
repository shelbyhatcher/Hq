import os
import time
import logging
import asyncio
from datetime import datetime

from app.core.db import SessionLocal
from app.services.reddit_ingest import MONITORED_SUBREDDITS, RedditIngestionError, ingest_and_persist_subreddit

# Configure logging — always stream to stdout; add file handler only if /tmp is writable
_log_handlers: list = [logging.StreamHandler()]
try:
    _log_handlers.append(logging.FileHandler("/tmp/trendcatcher_scheduler.log"))
except (PermissionError, OSError):
    pass  # Skip file logging if /tmp is not writable (e.g. restricted sandbox env)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=_log_handlers,
)
logger = logging.getLogger("TrendCatcherScheduler")

# Global scheduler state — updated by run_scheduler_loop_async so the
# admin dashboard can report "green" for the in-process background task.
scheduler_status = {
    "running": False,
    "last_scan_at": None,  # ISO datetime string of last successful scan
    "cycles_completed": 0,
    "last_verified_reddit_writes": 0,
    "last_verified_reddit_updates": 0,
    "last_reddit_errors": [],
}


async def scan_and_evaluate_trends():
    """Fetch and persist only verified Reddit public JSON trend signals.

    Earlier builds generated random platform scores and persisted those rows as
    trends. The public app must not present simulated data as live, so this
    scheduler now writes only rows fetched from Reddit public JSON with explicit
    provenance. Reddit errors are logged honestly and produce no live writes.
    """
    logger.info("Starting TrendCatcher verified Reddit public JSON trend scan...")
    limit = int(os.getenv("REDDIT_SCHEDULER_LIMIT_PER_SUBREDDIT", "10"))
    sort = os.getenv("REDDIT_SCHEDULER_SORT", "rising")

    db = SessionLocal()
    written_total = 0
    updated_total = 0
    errors = []
    try:
        for subreddit in MONITORED_SUBREDDITS:
            try:
                result = await ingest_and_persist_subreddit(db, subreddit, limit=limit, sort=sort)
                written_total += result.written_trends
                updated_total += result.updated_trends
                logger.info(
                    "Verified Reddit ingestion r/%s fetched=%s written=%s updated=%s skipped=%s",
                    result.subreddit,
                    result.fetched_posts,
                    result.written_trends,
                    result.updated_trends,
                    result.skipped_posts,
                )
            except RedditIngestionError as exc:
                db.rollback()
                message = f"r/{subreddit}: {exc}"
                errors.append(message)
                logger.warning("Verified Reddit ingestion skipped: %s", message)
    finally:
        db.close()

    scheduler_status["last_verified_reddit_writes"] = written_total
    scheduler_status["last_verified_reddit_updates"] = updated_total
    scheduler_status["last_reddit_errors"] = errors[:5]

    if written_total == 0 and updated_total == 0:
        logger.warning(
            "Verified Reddit scan completed with no live trend writes. "
            "The public feed remains empty or unchanged unless verified provenance rows already exist."
        )


def run_scheduler_loop(interval_seconds: int = 86400):
    """
    Runs the trendcatcher autonomous scheduler in a background loop.
    Default interval is 24 hours (86400 seconds).
    """
    logger.info(f"Starting autonomous scheduler background daemon loop (Interval: {interval_seconds}s)...")
    while True:
        try:
            asyncio.run(scan_and_evaluate_trends())
        except Exception as e:
            logger.error(f"Error in scheduler execution cycle: {str(e)}")
        logger.info(f"Sleeping for {interval_seconds} seconds until next cycle...")
        time.sleep(interval_seconds)


async def run_scheduler_loop_async(interval_seconds: int = 86400):
    """
    Non-blocking async loop to run the scheduler inside FastAPI startup/lifespan context.
    """
    logger.info(f"Starting autonomous scheduler background async loop (Interval: {interval_seconds}s)...")
    scheduler_status["running"] = True
    # Wait a short duration on startup to ensure FastAPI app is fully booted and listening
    await asyncio.sleep(10)
    while True:
        try:
            logger.info("Triggering periodic verified Reddit trend scan...")
            await scan_and_evaluate_trends()
            scheduler_status["last_scan_at"] = datetime.utcnow().isoformat()
            scheduler_status["cycles_completed"] += 1
        except Exception as e:
            logger.error(f"Error in async scheduler execution cycle: {str(e)}")
        logger.info(f"Sleeping for {interval_seconds} seconds until next async cycle...")
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    import sys
    print("====================================================")
    print("TrendCatcher Verified Reddit Public JSON Scheduler")
    print("====================================================")

    # Check arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # Run as loop (default interval 24 hours, or specified)
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 86400
        run_scheduler_loop(interval)
    else:
        # Run once and exit
        asyncio.run(scan_and_evaluate_trends())
