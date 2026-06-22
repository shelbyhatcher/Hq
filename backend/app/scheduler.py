import os
import time
import httpx
import logging
import random
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from app.core.db import SessionLocal
from app.models import db_models

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

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000/api")
BLOG_BASE_URL = os.getenv("BLOG_BASE_URL", "http://localhost:5000/api")
TRACKING_ID = "trendcatcher-20"

# Target products/keywords list with category designations
TARGET_PRODUCTS = [
    {"name": "Aesthetic Smart Mug", "category": "Home Goods"},
    {"name": "Minimalist Desk Organizer", "category": "Home Goods"},
    {"name": "Viral Scalp Massager", "category": "Beauty & Skincare"},
    {"name": "Korean Glass Skin Serum", "category": "Beauty & Skincare"},
    {"name": "Aesthetic MagSafe Stand", "category": "Electronics"},
    {"name": "Noise Cancelling Budget Earbuds", "category": "Electronics"}
]

async def scan_and_evaluate_trends():
    logger.info("Starting TrendCatcher autonomous trend scan...")
    
    async with httpx.AsyncClient() as client:
        # Check API health
        try:
            health_check = await client.get(f"{API_BASE_URL}/health")
            if health_check.status_code != 200:
                logger.error(f"FastAPI engine is unhealthy: {health_check.text}")
                return
        except Exception as e:
            logger.error(f"Cannot connect to FastAPI engine on {API_BASE_URL}: {str(e)}")
            return

        published_count = 0
        
        for prod in TARGET_PRODUCTS:
            name = prod["name"]
            category = prod["category"]
            logger.info(f"Scanning social signals for: '{name}' ({category})...")
            
            # 1. Simulate platform-specific scores
            # Under live production, these would scrape TikTok, Pinterest, Reddit, Instagram.
            # We generate simulated scores with random variance matching typical emerging/viral trends.
            tiktok_score = round(random.uniform(5.0, 9.8), 1)
            instagram_score = round(random.uniform(6.0, 9.9), 1)
            pinterest_score = round(random.uniform(4.5, 9.5), 1)
            reddit_score = round(random.uniform(4.0, 9.2), 1)
            
            # 2. Call Scoring Engine endpoint to calculate CVS
            score_payload = {
                "tiktok_score": tiktok_score,
                "instagram_score": instagram_score,
                "pinterest_score": pinterest_score,
                "reddit_score": reddit_score
            }
            
            try:
                score_response = await client.post(f"{API_BASE_URL}/trends/score", params=score_payload)
                if score_response.status_code == 200:
                    score_data = score_response.json()
                    cvs_score = score_data.get("composite_virality_score", 0.0)
                    logger.info(f"Calculated CVS for '{name}': {cvs_score}/10")
                else:
                    logger.error(f"Failed to calculate CVS: {score_response.text}")
                    continue
            except Exception as e:
                logger.error(f"CVS request failed: {str(e)}")
                continue
                
            # 3. Simulate comment-sentiment PIR (Purchase Intent Ratio)
            pir_score = round(random.uniform(0.65, 0.95), 2)
            logger.info(f"PIR Sentiment Score for '{name}': {pir_score:.0%}")
            
            # Write/Update result directly to persistent database
            db = SessionLocal()
            try:
                # Find the product by name
                db_prod = db.query(db_models.Product).filter(db_models.Product.name == name).first()
                if not db_prod:
                    db_prod = db_models.Product(
                        name=name,
                        category=category,
                        description=f"Automated scan product: {name}",
                        estimated_price=29.99
                    )
                    db.add(db_prod)
                    db.commit()
                    db.refresh(db_prod)

                # Update or create Trend record
                db_trend = db.query(db_models.Trend).filter(db_models.Trend.product_id == db_prod.id).first()
                status = "emerging" if cvs_score >= 8.0 else "monitored"
                if db_trend:
                    db_trend.velocity_score = cvs_score
                    db_trend.purchase_intent_ratio = pir_score
                    db_trend.status = status
                    db_trend.scanned_at = datetime.utcnow()
                else:
                    db_trend = db_models.Trend(
                        product_id=db_prod.id,
                        velocity_score=cvs_score,
                        purchase_intent_ratio=pir_score,
                        status=status,
                        access_level="public",
                        scanned_at=datetime.utcnow()
                    )
                    db.add(db_trend)
                db.commit()
                logger.info(f"Successfully persisted Trend data in DB for '{name}'")
            except Exception as db_err:
                db.rollback()
                logger.error(f"Failed to save Trend data to DB for '{name}': {db_err}")
            finally:
                db.close()
            
            # 4. Check against locked production thresholds (CVS >= 8.0, PIR >= 0.80)
            if cvs_score >= 8.0 and pir_score >= 0.80:
                logger.info(f"🌟 EMERGING TREND CONFIRMED: '{name}' qualifies for automated auto-publishing!")
                
                # Define key features for content generation
                features_map = {
                    "Aesthetic Smart Mug": ["Self-heating base", "Temperature-controlled LED", "Spill-proof design"],
                    "Minimalist Desk Organizer": ["Premium solid oak", "Modular compartments", "Magnetic phone dock"],
                    "Viral Scalp Massager": ["Soft silicone bristles", "Ergonomic finger grip", "Deep exfoliation"],
                    "Korean Glass Skin Serum": ["Niacinamide active base", "Snail mucin extraction", "Dewy 24h hydration"],
                    "Aesthetic MagSafe Stand": ["Heavy aluminum build", "360-degree rotation", "Hidden cable routing"],
                    "Noise Cancelling Budget Earbuds": ["Active ANC hybrid", "35h battery lifespan", "Sub-$50 high-fidelity"]
                }
                
                features = features_map.get(name, ["Viral-grade aesthetic finish", "High social engagement rating", "Ergonomic usability"])
                estimated_price = random.choice([24.99, 39.50, 49.99, 64.99])
                
                content_payload = {
                    "product_name": name,
                    "category": category,
                    "features": features,
                    "estimated_price": estimated_price,
                    "cvs_score": cvs_score,
                    "pir_score": pir_score,
                    "affiliate_tracking_id": TRACKING_ID,
                    "publish_to_blog": True
                }
                
                try:
                    logger.info(f"Invoking AI Content Engine and Handshake Blog API to post '{name}'...")
                    publish_response = await client.post(f"{API_BASE_URL}/ai/generate-content", json=content_payload, timeout=25.0)
                    
                    if publish_response.status_code == 200:
                        publish_data = publish_response.json()
                        publish_status = publish_data.get("publish_status", {})
                        
                        if publish_status.get("success"):
                            url = publish_status.get("published_url")
                            logger.info(f"✅ SUCCESS: Post published successfully for '{name}' at: {url}")
                            published_count += 1
                        else:
                            logger.error(f"❌ Handshake failed: {publish_status.get('error')}")
                    else:
                        logger.error(f"❌ Generative request failed: {publish_response.text}")
                except Exception as e:
                    logger.error(f"Handshake request failed for '{name}': {str(e)}")
            else:
                logger.info(f"Trend '{name}' monitored. Did not cross Locked Virality Threshold (CVS: {cvs_score}/8.0, PIR: {pir_score:.0%}/80%).")
                
        logger.info(f"Scan complete. Published {published_count} new trend articles autonomously.")

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
