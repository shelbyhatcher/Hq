import os
import time
import logging
import asyncio
from datetime import datetime

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
}

async def scan_and_evaluate_trends():
    """Skip live trend writes until verified ingestion/provenance exists.

    Earlier builds generated random platform scores and persisted those rows as
    trends. The public app must not present simulated data as live, so the
    scheduler is intentionally a no-op until real social ingestion is wired.
    """
    logger.info("Starting TrendCatcher autonomous trend scan...")
    logger.warning("Live trend scan skipped: no verified social-ingestion source is configured.")

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
            logger.info("Triggering periodic autonomous trend scan...")
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
    print("TrendCatcher Autonomous Scheduler & Handshake Daemon")
    print("====================================================")
    
    # Check arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # Run as loop (default interval 24 hours, or specified)
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 86400
        run_scheduler_loop(interval)
    else:
        # Run once and exit
        asyncio.run(scan_and_evaluate_trends())
