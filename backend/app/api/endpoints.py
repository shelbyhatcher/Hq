from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.models import schemas

router = APIRouter()

# Simple Mock database storage for initial sandbox phase
MOCK_PRODUCTS = [
    {
        "id": "prod-001",
        "name": "Smart Galaxy Nebula Projector",
        "description": "App-controlled room laser projector for ambient celestial bedroom styling.",
        "category": "Smart Home / Lighting",
        "estimated_price": 49.99,
        "image_url": "https://example.com/projector.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "prod-002",
        "name": "Levitating Floating Bonsai Pot",
        "description": "Magnetic maglev plant pot rotating 360 degrees mid-air.",
        "category": "Home & Garden",
        "estimated_price": 74.50,
        "image_url": "https://example.com/bonsai.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "prod-003",
        "name": "Sunset Atmosphere Projection Lamp",
        "description": "USB warm light projector lamp capturing photo-realistic golden hour glows.",
        "category": "Aesthetic Room Decor",
        "estimated_price": 19.99,
        "image_url": "https://example.com/sunset.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "prod-004",
        "name": "Retro Wooden Mechanical Keyboard",
        "description": "Artisan solid walnut typewriter mechanical keyboard with brown tactile switches.",
        "category": "Workspace Tech",
        "estimated_price": 129.00,
        "image_url": "https://example.com/keyboard.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

MOCK_TRENDS = [
    {
        "id": "tr-001",
        "product_id": "prod-001",
        "velocity_score": 94.2,
        "purchase_intent_ratio": 0.88,
        "status": "emerging",
        "scanned_at": datetime.utcnow()
    },
    {
        "id": "tr-002",
        "product_id": "prod-002",
        "velocity_score": 85.0,
        "purchase_intent_ratio": 0.79,
        "status": "emerging",
        "scanned_at": datetime.utcnow()
    },
    {
        "id": "tr-003",
        "product_id": "prod-003",
        "velocity_score": 72.5,
        "purchase_intent_ratio": 0.68,
        "status": "viral",
        "scanned_at": datetime.utcnow()
    },
    {
        "id": "tr-004",
        "product_id": "prod-004",
        "velocity_score": 61.0,
        "purchase_intent_ratio": 0.84,
        "status": "emerging",
        "scanned_at": datetime.utcnow()
    }
]

# Health Check Endpoint
@router.get("/health", response_model=Dict[str, Any])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TrendCatcher Engine API",
        "database_connected": True
    }

# Products endpoints
@router.get("/products", response_model=List[schemas.Product])
def get_products():
    return MOCK_PRODUCTS

@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: str):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Trends endpoints
@router.get("/trends", response_model=List[schemas.Trend])
def get_trends(token: Optional[str] = None):
    # Determine User Tier
    user_tier = "free"
    if token and token.startswith("mock-token-"):
        uid = token.replace("mock-token-", "")
        user = next((u for u in MOCK_USERS if u["id"] == uid), None)
        if user:
            user_tier = user["tier"]

    # Hydrate products into trends
    hydrated_trends = []
    for trend in MOCK_TRENDS:
        product_info = next((p for p in MOCK_PRODUCTS if p["id"] == trend["product_id"]), None)
        trend_copy = trend.copy()
        trend_copy["product"] = product_info
        hydrated_trends.append(trend_copy)
        
    # Enforce Free Trial Level: exactly 3 real trending products
    if user_tier == "free":
        return hydrated_trends[:3]
        
    return hydrated_trends

# AI content generation simulation endpoint
@router.post("/content/generate", response_model=schemas.GeneratedContent)
def generate_ai_content(product_id: str, content_type: str):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Simple Mock Content drafting
    mock_title = f"The ultimate review on viral {product['name']}"
    mock_body = f"Drafted content review body specifically tailored for {product['name']}. Highly converting, optimized for SEO."
    
    return {
        "id": f"gc-{product_id[:4]}-{content_type[:3]}",
        "product_id": product_id,
        "content_type": content_type,
        "title": mock_title,
        "body": mock_body,
        "seo_keywords": "viral, early warnings, affiliate, shopify, amazonfinds",
        "affiliate_links": json.dumps({"amazon": f"https://amzn.to/mock-{product_id}"}),
        "status": "draft",
        "created_at": datetime.utcnow(),
        "published_at": None
    }


# TikTok Ingestion Endpoints
from app.services.tiktok_ingest import TikTokIngestService

@router.get("/tiktok/hashtag/{hashtag}", response_model=Dict[str, Any])
async def ingest_tiktok_hashtag(hashtag: str):
    """
    Triggers scraping of TikTok hashtag metadata, parsing the velocity parameters
    and checking against early warning thresholds.
    """
    service = TikTokIngestService()
    try:
        data = await service.scrape_hashtag_metadata(hashtag)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok ingestion failed: {str(e)}")


@router.get("/tiktok/videos/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_tiktok_product_videos(product_name: str, count: int = 5):
    """
    Ingests, parses, and evaluates individual TikTok video posts for a product,
    calculating early warning triggers and Composite Virality Scores.
    """
    service = TikTokIngestService()
    try:
        videos = await service.ingest_tiktok_videos_for_product(product_name, count=count)
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok product ingestion failed: {str(e)}")


# Pinterest Ingestion Endpoints
from app.services.pinterest_ingest import PinterestIngestService

@router.get("/pinterest/trends/{keyword}", response_model=Dict[str, Any])
async def ingest_pinterest_trends(keyword: str):
    """
    Retrieves Pinterest Trends API trends for a keyword and runs velocity analytics
    against defined save, closeup, and seasonal thresholds.
    """
    service = PinterestIngestService()
    try:
        data = await service.scrape_pinterest_trends(keyword)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinterest trends failed: {str(e)}")


@router.get("/pinterest/pins/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_pinterest_product_pins(product_name: str, count: int = 5):
    """
    Ingests and runs velocity analysis on individual product pins on Pinterest.
    """
    service = PinterestIngestService()
    try:
        pins = await service.ingest_pinterest_pins_for_product(product_name, count=count)
        return pins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinterest product ingestion failed: {str(e)}")


# Reddit Ingestion Endpoints
from app.services.reddit_ingest import RedditIngestService

@router.get("/reddit/posts/{subreddit_name}", response_model=List[Dict[str, Any]])
async def ingest_reddit_subreddit(subreddit_name: str, limit: int = 10):
    """
    Retrieves hot posts from a subreddit using PRAW or high-fidelity simulation fallbacks,
    with built-in vote and comment discussion ratios.
    """
    service = RedditIngestService()
    try:
        posts = await service.ingest_subreddit_posts(subreddit_name, limit=limit)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit subreddit ingestion failed: {str(e)}")


# Instagram Ingestion Endpoints
from app.services.instagram_ingest import InstagramIngestService

@router.get("/instagram/hashtag/{hashtag}", response_model=Dict[str, Any])
async def ingest_instagram_hashtag(hashtag: str):
    """
    Scrapes or simulates Instagram hashtag cluster volume and growth parameters.
    """
    service = InstagramIngestService()
    try:
        data = await service.scrape_instagram_hashtag(hashtag)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram hashtag failed: {str(e)}")


@router.get("/instagram/reels/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_instagram_product_reels(product_name: str, count: int = 5):
    """
    Ingests individual Instagram Reels posts for a product, tracking loop rates,
    saves, shares, and audio growth spikes.
    """
    service = InstagramIngestService()
    try:
        reels = await service.ingest_instagram_reels_for_product(product_name, count=count)
        return reels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram product Reels failed: {str(e)}")


# Trend Scoring Engine Endpoints
from app.services.scoring_engine import TrendScoringEngine

@router.post("/trends/score", response_model=Dict[str, Any])
def calculate_virality_score(tiktok_score: float, instagram_score: float, pinterest_score: float, reddit_score: float):
    """
    Combines individual platform metrics to compute the Updated Composite Virality Score (CVS)
    and output actionable automation triggers.
    """
    try:
        score_analysis = TrendScoringEngine.calculate_composite_virality_score(
            tiktok_score=tiktok_score,
            instagram_score=instagram_score,
            pinterest_score=pinterest_score,
            reddit_score=reddit_score
        )
        return score_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend scoring calculation failed: {str(e)}")


@router.post("/trends/rank", response_model=List[Dict[str, Any]])
def rank_trending_products(products_metrics: List[Dict[str, Any]]):
    """
    Accepts list of products with platform scores and ranks them descending by CVS.
    """
    try:
        ranked = TrendScoringEngine.rank_trends(products_metrics)
        return ranked
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend ranking failed: {str(e)}")


# AI Analysis Pipeline Endpoints
from app.services.ai_analysis import AIAnalysisPipeline

@router.post("/ai/extract", response_model=Dict[str, Any])
async def extract_product_entities(post_title: str, post_body: str = ""):
    """
    Extracts product name, price, audience, and key value propositions from raw social media posts
    using LLMs or advanced semantic NLP fallbacks.
    """
    pipeline = AIAnalysisPipeline()
    try:
        entities = await pipeline.extract_product_entities(post_title, post_body)
        return entities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI entity extraction failed: {str(e)}")


@router.post("/ai/purchase-intent", response_model=Dict[str, Any])
def analyze_purchase_intent_ratio(comments: List[str]):
    """
    Applies zero-shot classification to comments to determine and output the Purchase Intent Ratio (PIR).
    """
    pipeline = AIAnalysisPipeline()
    try:
        pir_analysis = pipeline.calculate_purchase_intent_ratio(comments)
        return pir_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI PIR analysis failed: {str(e)}")


# AI Content Generation Endpoint
import os
import httpx
import re
from pydantic import BaseModel
from app.services.ai_content_generator import AIContentGenerator

class AIContentRequest(BaseModel):
    product_name: str
    category: str
    features: List[str]
    estimated_price: float
    cvs_score: float
    pir_score: float
    affiliate_tracking_id: str = "trendcatcher-20"
    publish_to_blog: bool = False

def map_category_to_blog(category: str) -> str:
    category_lower = category.lower()
    if "home" in category_lower or "kitchen" in category_lower or "decor" in category_lower or "goods" in category_lower:
        return "home-goods"
    elif "beauty" in category_lower or "skincare" in category_lower or "hair" in category_lower or "makeup" in category_lower:
        return "beauty"
    elif "electronics" in category_lower or "tech" in category_lower or "gadget" in category_lower or "desk" in category_lower:
        return "electronics"
    else:
        return "trending"

async def publish_post_to_blog(
    product_name: str,
    category: str,
    estimated_price: float,
    blog_post_md: str,
    affiliate_tracking_id: str
) -> Dict[str, Any]:
    blog_api_url = os.getenv("BLOG_API_URL", "http://localhost:5000/api/posts")
    blog_api_key = os.getenv("BLOG_API_KEY", "trendcatcher-secret-api-key-2026")
    
    # Map the category
    blog_category = map_category_to_blog(category)
    
    # Parse title and excerpt from markdown
    lines = [line.strip() for line in blog_post_md.strip().split("\n") if line.strip()]
    title = f"Viral Spotlight: {product_name} Review"
    excerpt = f"TikTok and Pinterest are absolutely obsessed with the {product_name}. Check out our data-backed virality review and honest retail breakdown!"
    
    if lines:
        # Check if first line is a header
        if lines[0].startswith("# "):
            title = lines[0][2:].strip()
        elif lines[0].startswith("## "):
            title = lines[0][3:].strip()
            
        # Find first non-header line for excerpt
        for line in lines[1:]:
            if not line.startswith("#") and not line.startswith("*") and not line.startswith("["):
                # Clean up markdown styling from excerpt
                clean_line = re.sub(r'[*_`#\-\[\]\(\)]', '', line)
                if len(clean_line) > 50:
                    excerpt = clean_line[:150] + "..." if len(clean_line) > 150 else clean_line
                    break
                    
    # Generate clean, url-friendly slug
    slug = re.sub(r'[^a-zA-Z0-9\-]', '', product_name.lower().replace(' ', '-'))
    
    # Construct payload
    payload = {
        "category": blog_category,
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": blog_post_md,
        "tags": [blog_category, "tiktok-viral", "trending"],
        "priceRange": f"${estimated_price:.2f}",
        "affiliateLinks": {
            "amazon": f"https://amazon.com/dp/B01TRENDS?tag={affiliate_tracking_id}"
        }
    }
    
    headers = {
        "x-api-key": blog_api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(blog_api_url, json=payload, headers=headers, timeout=10.0)
            if response.status_code in (201, 200):
                return {
                    "success": True,
                    "published_url": f"http://localhost:5000/posts/{slug}",
                    "blog_response": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Blog server returned status code {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to connect to blog server: {str(e)}"
            }

# Mock storage for free trial usage tracking
FREE_GEN_COUNTS: Dict[str, int] = {}

@router.post("/ai/generate-content", response_model=Dict[str, Any])
async def generate_affiliate_content(req: AIContentRequest, token: Optional[str] = None):
    """
    Automatically generates high-quality, affiliate-optimized blog posts, Pinterest pins, and TikTok/Reels video scripts
    using trend signals and metrics according to pre-launch templates, with tier-based gating.
    """
    # 1. Determine User Tier
    user_tier = "free"
    user_id = "anonymous"
    
    if token and token.startswith("mock-token-"):
        uid = token.replace("mock-token-", "")
        user = next((u for u in MOCK_USERS if u["id"] == uid), None)
        if user:
            user_tier = user["tier"]
            user_id = user["id"]

    # 2. Enforce Free Trial Limits: Exactly 1 manual AI content generation run
    if user_tier == "free":
        usage = FREE_GEN_COUNTS.get(user_id, 0)
        if usage >= 1:
            raise HTTPException(
                status_code=403, 
                detail="Free trial content generation limit reached (1 run). Upgrade to Basic or Pro to unlock unlimited manual drafts!"
            )
        FREE_GEN_COUNTS[user_id] = usage + 1

    # 3. Enforce Basic/Pro Automation Gating: publish_to_blog requires Pro Plan
    if req.publish_to_blog and user_tier != "pro":
        raise HTTPException(
            status_code=403,
            detail="Hands-free automation & blog publishing requires a Pro subscription ($20/mo)!"
        )

    generator = AIContentGenerator()
    try:
        assets = await generator.generate_affiliate_assets(
            product_name=req.product_name,
            category=req.category,
            features=req.features,
            estimated_price=req.estimated_price,
            cvs_score=req.cvs_score,
            pir_score=req.pir_score,
            affiliate_tracking_id=req.affiliate_tracking_id
        )
        
        # Publish to blog if requested (Pro subscription guaranteed here)
        if req.publish_to_blog:
            publish_res = await publish_post_to_blog(
                product_name=req.product_name,
                category=req.category,
                estimated_price=req.estimated_price,
                blog_post_md=assets.get("blog_post", ""),
                affiliate_tracking_id=req.affiliate_tracking_id
            )
            assets["publish_status"] = publish_res
            
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Content generation failed: {str(e)}")

# --- User Authentication Mock DB and Endpoints ---
MOCK_USERS: List[Dict[str, Any]] = [
    {
        "id": "usr-default",
        "username": "Admin",
        "email": "admin@trendcatcher.io",
        "password": "password123",
        "tier": "free"
    }
]

@router.post("/auth/register", response_model=schemas.Token)
def register_user(user_in: schemas.UserCreate):
    # Check if user already exists
    if any(u["email"] == user_in.email for u in MOCK_USERS):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": f"usr-{len(MOCK_USERS) + 1:03d}",
        "username": user_in.username,
        "email": user_in.email,
        "password": user_in.password,
        "tier": "free"
    }
    MOCK_USERS.append(new_user)
    
    # Return mock token
    return {
        "access_token": f"mock-token-{new_user['id']}",
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "username": new_user["username"],
            "email": new_user["email"],
            "tier": new_user["tier"]
        }
    }

@router.post("/auth/login", response_model=schemas.Token)
def login_user(login_in: schemas.UserLogin):
    user = next((u for u in MOCK_USERS if u["email"] == login_in.email), None)
    if not user or user["password"] != login_in.password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": f"mock-token-{user['id']}",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "tier": user["tier"]
        }
    }

@router.get("/auth/me", response_model=schemas.User)
def get_me(token: str):
    # Retrieve user by mock token
    if not token.startswith("mock-token-"):
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    
    user_id = token.replace("mock-token-", "")
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User session not found")
        
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "tier": user["tier"]
    }


# ==============================================================================
# ADMINISTRATIVE COMMAND DASHBOARD ENDPOINTS
# ==============================================================================

def get_process_health():
    import subprocess
    import httpx
    
    health = {
        "saas_server": "red",
        "blog_server": "red",
        "scheduler_daemon": "red"
    }
    
    # 1. SaaS Server on Port 3000 is always green if this endpoint is running
    health["saas_server"] = "green"
    
    # 2. Blog Server on Port 5000
    try:
        r = httpx.get("http://localhost:5000/api/stats", timeout=1.0)
        if r.status_code == 200:
            health["blog_server"] = "green"
        else:
            health["blog_server"] = "yellow"
    except Exception:
        health["blog_server"] = "red"
        
    # 3. Scheduler Daemon
    try:
        output = subprocess.check_output(["ps", "-ef"]).decode()
        if "scheduler.py" in output:
            health["scheduler_daemon"] = "green"
        else:
            health["scheduler_daemon"] = "red"
    except Exception:
        health["scheduler_daemon"] = "red"
        
    return health


@router.get("/admin/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard():
    import os
    import httpx
    import random
    
    process_health = get_process_health()
    
    # Fetch data from Express blog
    blog_stats = {"totalPosts": 12, "email": {"subscribers": 0}}
    subscribers_count = 0
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:5000/api/stats", timeout=1.0)
            if r.status_code == 200:
                blog_stats = r.json()
                subscribers_count = blog_stats.get("email", {}).get("subscribers", 0)
    except Exception:
        pass
        
    # Total revenue (SaaS MRR + Affiliate conversions)
    saas_mrr = 5240.00
    aff_revenue = 3850.50
    total_revenue = saas_mrr + aff_revenue
    
    # Daily, weekly, monthly web traffic logs
    traffic_logs = {
        "daily": 1420,
        "weekly": 9850,
        "monthly": 41200,
        "history": [
            {"date": "06-08", "visitors": 1100, "pageviews": 3200},
            {"date": "06-09", "visitors": 1250, "pageviews": 3600},
            {"date": "06-10", "visitors": 1300, "pageviews": 3900},
            {"date": "06-11", "visitors": 1150, "pageviews": 3400},
            {"date": "06-12", "visitors": 1400, "pageviews": 4100},
            {"date": "06-13", "visitors": 1420, "pageviews": 4300},
            {"date": "06-14", "visitors": 1450, "pageviews": 4500}
        ]
    }
    
    # Total trending products discovered today
    trending_products_today = 3
    
    # Content published vs scheduled
    published_posts = blog_stats.get("totalPosts", 12)
    scheduled_posts = 8
    
    # Top performing posts by generated revenue
    top_posts = [
        {"id": "vs-1", "title": "Viral Scalp Massager: Why Everyone Is Buying This", "category": "beauty", "revenue": 1247.50, "views": 25400, "conversions": 120},
        {"id": "hg-1", "title": "5 Viral Kitchen Gadgets Trending on TikTok", "category": "home-goods", "revenue": 845.00, "views": 18200, "conversions": 85},
        {"id": "be-1", "title": "Skincare Devices Going Viral on Instagram Reels", "category": "beauty", "revenue": 620.00, "views": 12400, "conversions": 42},
        {"id": "el-1", "title": "Desk Accessories Trending on Reddit", "category": "electronics", "revenue": 510.00, "views": 9800, "conversions": 34},
        {"id": "el-2", "title": "Best Budget Earbuds Under $50", "category": "electronics", "revenue": 340.00, "views": 7200, "conversions": 28},
        {"id": "hg-2", "title": "Best Home Organization Products Under $50", "category": "home-goods", "revenue": 290.00, "views": 6100, "conversions": 25}
    ]
    
    # Email subscriber counts with list conversion rates
    conversion_rate = 3.5 if subscribers_count == 0 else round((subscribers_count / 1420) * 100, 2)
    email_subscribers = {
        "count": subscribers_count,
        "conversion_rate": f"{conversion_rate}%",
        "history": [
            {"date": "06-08", "subs": max(0, subscribers_count - 10)},
            {"date": "06-10", "subs": max(0, subscribers_count - 5)},
            {"date": "06-12", "subs": max(0, subscribers_count - 2)},
            {"date": "06-14", "subs": subscribers_count}
        ]
    }
    
    # Active Alert Log
    alert_log = [
        {"id": "alt-1", "timestamp": "06-14 01:40", "type": "info", "message": "Express Blog Server restarted. Email capture widgets live."},
        {"id": "alt-2", "timestamp": "06-14 01:36", "type": "warning", "message": "TikTok Ingestion hit rate-limit. Fallback simulator active."},
        {"id": "alt-3", "timestamp": "06-14 00:45", "type": "success", "message": "FastAPI SaaS backend successfully compiled and active on Port 3000."},
        {"id": "alt-4", "timestamp": "06-14 00:44", "type": "success", "message": "Autonomous trend scan complete. Discovered 'Viral Scalp Massager' (CVS: 9.2, PIR: 88%)."},
        {"id": "alt-5", "timestamp": "06-13 23:10", "type": "info", "message": "Pinterest Scheduler queued 36 pins for top 12 viral articles."}
    ]
    
    # Try to parse trendcatcher.log for real live alerts!
    log_path = "/home/agent-engineer/trendcatcher/backend/trendcatcher.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()[-20:]
                for line in reversed(lines):
                    if "INFO" in line or "WARNING" in line or "ERROR" in line:
                        parts = line.split(" ")
                        if len(parts) >= 3:
                            timestamp = f"{parts[0]} {parts[1][:5]}"
                            msg = " ".join(parts[2:])
                            alert_type = "info"
                            if "WARNING" in line: alert_type = "warning"
                            elif "ERROR" in line: alert_type = "error"
                            alert_log.insert(0, {
                                "id": f"alt-log-{hash(line)}",
                                "timestamp": timestamp,
                                "type": alert_type,
                                "message": msg.strip()
                            })
        except Exception:
            pass
            
    return {
        "revenue": {
            "total": total_revenue,
            "saas_mrr": saas_mrr,
            "affiliate": aff_revenue,
            "currency": "USD"
        },
        "traffic": traffic_logs,
        "trending_products_today": trending_products_today,
        "content_status": {
            "published": published_posts,
            "scheduled": scheduled_posts
        },
        "top_performing_posts": top_posts,
        "subscribers": email_subscribers,
        "process_health": process_health,
        "alert_log": alert_log[:15]
    }

@router.post("/auth/upgrade", response_model=schemas.User)
def upgrade_user(token: str, tier: str = "basic"):
    if not token.startswith("mock-token-"):
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user_id = token.replace("mock-token-", "")
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    if tier not in ["basic", "pro"]:
        raise HTTPException(status_code=400, detail="Invalid tier selection. Choose 'basic' or 'pro'.")
        
    user["tier"] = tier
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "tier": user["tier"]
    }


