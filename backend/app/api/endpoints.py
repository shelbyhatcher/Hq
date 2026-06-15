import json
import os
import re
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import db_models, schemas
from app.services.ai_analysis import AIAnalysisPipeline
from app.services.ai_content_generator import AIContentGenerator
from app.services.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.services.instagram_ingest import InstagramIngestService
from app.services.pinterest_ingest import PinterestIngestService
from app.services.reddit_ingest import RedditIngestService
from app.services.scoring_engine import TrendScoringEngine
from app.services.tiktok_ingest import TikTokIngestService

router = APIRouter()

MOCK_PRODUCTS = [
    {
        "id": "prod-001",
        "name": "Smart Galaxy Nebula Projector",
        "description": "App-controlled room laser projector for ambient celestial bedroom styling.",
        "category": "Smart Home / Lighting",
        "estimated_price": 49.99,
        "image_url": "https://example.com/projector.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": "prod-002",
        "name": "Levitating Floating Bonsai Pot",
        "description": "Magnetic maglev plant pot rotating 360 degrees mid-air.",
        "category": "Home & Garden",
        "estimated_price": 74.50,
        "image_url": "https://example.com/bonsai.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": "prod-003",
        "name": "Sunset Atmosphere Projection Lamp",
        "description": "USB warm light projector lamp capturing photo-realistic golden hour glows.",
        "category": "Aesthetic Room Decor",
        "estimated_price": 19.99,
        "image_url": "https://example.com/sunset.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": "prod-004",
        "name": "Retro Wooden Mechanical Keyboard",
        "description": "Artisan solid walnut typewriter mechanical keyboard with brown tactile switches.",
        "category": "Workspace Tech",
        "estimated_price": 129.00,
        "image_url": "https://example.com/keyboard.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": "prod-005",
        "name": "Self-Heating Smart Mug",
        "description": "Rechargeable desk mug with app-based temperature control and spill-safe lid.",
        "category": "Workspace Tech",
        "estimated_price": 89.00,
        "image_url": "https://example.com/mug.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

MOCK_TRENDS = [
    {
        "id": "tr-001",
        "product_id": "prod-001",
        "velocity_score": 94.2,
        "purchase_intent_ratio": 0.88,
        "status": "emerging",
        "access_level": "public",
        "scanned_at": datetime.utcnow(),
    },
    {
        "id": "tr-002",
        "product_id": "prod-002",
        "velocity_score": 85.0,
        "purchase_intent_ratio": 0.79,
        "status": "emerging",
        "access_level": "public",
        "scanned_at": datetime.utcnow(),
    },
    {
        "id": "tr-003",
        "product_id": "prod-003",
        "velocity_score": 72.5,
        "purchase_intent_ratio": 0.68,
        "status": "viral",
        "access_level": "public",
        "scanned_at": datetime.utcnow(),
    },
    {
        "id": "tr-004",
        "product_id": "prod-004",
        "velocity_score": 61.0,
        "purchase_intent_ratio": 0.84,
        "status": "emerging",
        "access_level": "premium",
        "scanned_at": datetime.utcnow(),
    },
    {
        "id": "tr-005",
        "product_id": "prod-005",
        "velocity_score": 66.8,
        "purchase_intent_ratio": 0.81,
        "status": "emerging",
        "access_level": "premium",
        "scanned_at": datetime.utcnow(),
    },
]

FREE_GEN_COUNTS: Dict[str, int] = {}


class AIContentRequest(BaseModel):
    product_name: str
    category: str
    features: List[str]
    estimated_price: float
    cvs_score: float
    pir_score: float
    affiliate_tracking_id: str = "trendcatcher-20"
    publish_to_blog: bool = False


def serialize_user(user: db_models.User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "tier": user.tier,
    }


def extract_token(authorization: Optional[str], token: Optional[str] = None) -> Optional[str]:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return token


def get_user_from_request(
    db: Session,
    authorization: Optional[str] = None,
    token: Optional[str] = None,
) -> Optional[db_models.User]:
    access_token = extract_token(authorization, token)
    if not access_token:
        return None

    user_id = decode_access_token(access_token)
    if not user_id:
        return None
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()


def require_user(
    db: Session,
    authorization: Optional[str] = None,
    token: Optional[str] = None,
) -> db_models.User:
    user = get_user_from_request(db, authorization, token)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def is_paid_user(user: Optional[db_models.User]) -> bool:
    return bool(user and user.tier in {"basic", "pro"})


def build_trend_feed(user: Optional[db_models.User], include_locked: bool) -> List[Dict[str, Any]]:
    feed: List[Dict[str, Any]] = []
    paid = is_paid_user(user)

    for trend in MOCK_TRENDS:
        product_info = next((p for p in MOCK_PRODUCTS if p["id"] == trend["product_id"]), None)
        if not product_info:
            continue
        locked = trend["access_level"] == "premium" and not paid
        if locked and not include_locked:
            continue

        item = trend.copy()
        item["product"] = product_info
        item["locked"] = locked
        feed.append(item)

    return feed


@router.get("/health", response_model=Dict[str, Any])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TrendCatcher Engine API",
        "database_connected": True,
    }


@router.get("/products", response_model=List[schemas.Product])
def get_products():
    return MOCK_PRODUCTS


@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: str):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/trends", response_model=List[schemas.Trend])
def get_trends(
    include_locked: bool = False,
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    user = get_user_from_request(db, authorization, token)
    return build_trend_feed(user, include_locked)


@router.post("/content/generate", response_model=schemas.GeneratedContent)
def generate_ai_content(product_id: str, content_type: str):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": f"gc-{product_id[:4]}-{content_type[:3]}",
        "product_id": product_id,
        "content_type": content_type,
        "title": f"The ultimate review on viral {product['name']}",
        "body": f"Drafted content review body specifically tailored for {product['name']}. Highly converting, optimized for SEO.",
        "seo_keywords": "viral, early warnings, affiliate, shopify, amazonfinds",
        "affiliate_links": json.dumps({"amazon": f"https://amzn.to/mock-{product_id}"}),
        "status": "draft",
        "created_at": datetime.utcnow(),
        "published_at": None,
    }


@router.get("/tiktok/hashtag/{hashtag}", response_model=Dict[str, Any])
async def ingest_tiktok_hashtag(hashtag: str):
    service = TikTokIngestService()
    try:
        return await service.scrape_hashtag_metadata(hashtag)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TikTok ingestion failed: {exc}")


@router.get("/tiktok/videos/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_tiktok_product_videos(product_name: str, count: int = 5):
    service = TikTokIngestService()
    try:
        return await service.ingest_tiktok_videos_for_product(product_name, count=count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TikTok product ingestion failed: {exc}")


@router.get("/pinterest/trends/{keyword}", response_model=Dict[str, Any])
async def ingest_pinterest_trends(keyword: str):
    service = PinterestIngestService()
    try:
        return await service.scrape_pinterest_trends(keyword)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pinterest trends failed: {exc}")


@router.get("/pinterest/pins/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_pinterest_product_pins(product_name: str, count: int = 5):
    service = PinterestIngestService()
    try:
        return await service.ingest_pinterest_pins_for_product(product_name, count=count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pinterest product ingestion failed: {exc}")


@router.get("/reddit/posts/{subreddit_name}", response_model=List[Dict[str, Any]])
async def ingest_reddit_subreddit(subreddit_name: str, limit: int = 10):
    service = RedditIngestService()
    try:
        return await service.ingest_subreddit_posts(subreddit_name, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reddit subreddit ingestion failed: {exc}")


@router.get("/instagram/hashtag/{hashtag}", response_model=Dict[str, Any])
async def ingest_instagram_hashtag(hashtag: str):
    service = InstagramIngestService()
    try:
        return await service.scrape_instagram_hashtag(hashtag)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Instagram hashtag failed: {exc}")


@router.get("/instagram/reels/{product_name}", response_model=List[Dict[str, Any]])
async def ingest_instagram_product_reels(product_name: str, count: int = 5):
    service = InstagramIngestService()
    try:
        return await service.ingest_instagram_reels_for_product(product_name, count=count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Instagram product Reels failed: {exc}")


@router.post("/trends/score", response_model=Dict[str, Any])
def calculate_virality_score(
    tiktok_score: float,
    instagram_score: float,
    pinterest_score: float,
    reddit_score: float,
):
    try:
        return TrendScoringEngine.calculate_composite_virality_score(
            tiktok_score=tiktok_score,
            instagram_score=instagram_score,
            pinterest_score=pinterest_score,
            reddit_score=reddit_score,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trend scoring calculation failed: {exc}")


@router.post("/trends/rank", response_model=List[Dict[str, Any]])
def rank_trending_products(products_metrics: List[Dict[str, Any]]):
    try:
        return TrendScoringEngine.rank_trends(products_metrics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trend ranking failed: {exc}")


@router.post("/ai/extract", response_model=Dict[str, Any])
async def extract_product_entities(post_title: str, post_body: str = ""):
    pipeline = AIAnalysisPipeline()
    try:
        return await pipeline.extract_product_entities(post_title, post_body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI entity extraction failed: {exc}")


@router.post("/ai/purchase-intent", response_model=Dict[str, Any])
def analyze_purchase_intent_ratio(comments: List[str]):
    pipeline = AIAnalysisPipeline()
    try:
        return pipeline.calculate_purchase_intent_ratio(comments)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI PIR analysis failed: {exc}")


def map_category_to_blog(category: str) -> str:
    category_lower = category.lower()
    if any(token in category_lower for token in ["home", "kitchen", "decor", "goods"]):
        return "home-goods"
    if any(token in category_lower for token in ["beauty", "skincare", "hair", "makeup"]):
        return "beauty"
    if any(token in category_lower for token in ["electronics", "tech", "gadget", "desk"]):
        return "electronics"
    return "trending"


async def publish_post_to_blog(
    product_name: str,
    category: str,
    estimated_price: float,
    blog_post_md: str,
    affiliate_tracking_id: str,
) -> Dict[str, Any]:
    blog_api_url = os.getenv("BLOG_API_URL", "http://localhost:5000/api/posts")
    blog_api_key = os.getenv("BLOG_API_KEY", "")

    lines = [line.strip() for line in blog_post_md.strip().split("\n") if line.strip()]
    title = f"Viral Spotlight: {product_name} Review"
    excerpt = f"Data-backed review for {product_name}."
    if lines:
        if lines[0].startswith("# "):
            title = lines[0][2:].strip()
        elif lines[0].startswith("## "):
            title = lines[0][3:].strip()
        for line in lines[1:]:
            if not line.startswith("#") and not line.startswith("*") and not line.startswith("["):
                clean_line = re.sub(r'[*_`#\-\[\]\(\)]', '', line)
                if len(clean_line) > 20:
                    excerpt = clean_line[:150] + "..." if len(clean_line) > 150 else clean_line
                    break

    slug = re.sub(r'[^a-zA-Z0-9\-]', '', product_name.lower().replace(' ', '-'))
    payload = {
        "category": map_category_to_blog(category),
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": blog_post_md,
        "tags": [map_category_to_blog(category), "trending"],
        "priceRange": f"${estimated_price:.2f}",
        "affiliateLinks": {
            "amazon": f"https://amazon.com/dp/B01TRENDS?tag={affiliate_tracking_id}"
        },
    }

    headers = {"Content-Type": "application/json"}
    if blog_api_key:
        headers["x-api-key"] = blog_api_key

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(blog_api_url, json=payload, headers=headers, timeout=10.0)
            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "published_url": f"http://localhost:5000/posts/{slug}",
                    "blog_response": response.json(),
                }
            return {
                "success": False,
                "error": f"Blog server returned status code {response.status_code}: {response.text}",
            }
        except Exception as exc:
            return {"success": False, "error": f"Failed to connect to blog server: {exc}"}


@router.post("/ai/generate-content", response_model=Dict[str, Any])
async def generate_affiliate_content(
    req: AIContentRequest,
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    user = get_user_from_request(db, authorization, token)
    tier = user.tier if user else "free"
    user_id = user.id if user else "anonymous"

    if tier == "free":
        usage = FREE_GEN_COUNTS.get(user_id, 0)
        if usage >= 1:
            raise HTTPException(
                status_code=403,
                detail="Free users can generate one manual draft. Upgrade to Basic or Pro for more.",
            )
        FREE_GEN_COUNTS[user_id] = usage + 1

    if req.publish_to_blog and tier != "pro":
        raise HTTPException(
            status_code=403,
            detail="Hands-free publishing is reserved for Pro accounts.",
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
            affiliate_tracking_id=req.affiliate_tracking_id,
        )
        if req.publish_to_blog:
            assets["publish_status"] = await publish_post_to_blog(
                product_name=req.product_name,
                category=req.category,
                estimated_price=req.estimated_price,
                blog_post_md=assets.get("blog_post", ""),
                affiliate_tracking_id=req.affiliate_tracking_id,
            )
        return assets
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI Content generation failed: {exc}")


@router.post("/auth/register", response_model=schemas.Token)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(db_models.User).filter(db_models.User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = db_models.User(
        username=user_in.username.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hash_password(user_in.password),
        tier="free",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "access_token": create_access_token(new_user.id),
        "token_type": "bearer",
        "user": serialize_user(new_user),
    }


@router.post("/auth/login", response_model=schemas.Token)
def login_user(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.email == login_in.email.lower().strip()).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@router.get("/auth/me", response_model=schemas.User)
def get_me(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    user = require_user(db, authorization, token)
    return serialize_user(user)


@router.post("/auth/upgrade", response_model=schemas.User)
def upgrade_user(
    tier: str = "basic",
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    user = require_user(db, authorization, token)
    if tier not in {"basic", "pro", "free"}:
        raise HTTPException(status_code=400, detail="Invalid tier. Choose free, basic, or pro.")
    user.tier = tier
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.get("/subscription/plans", response_model=schemas.SubscriptionOverview)
def get_subscription_plans(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    user = get_user_from_request(db, authorization, token)
    return {
        "current_tier": user.tier if user else "free",
        "checkout_mode": "placeholder",
        "message": "Checkout links are managed outside the app. This tab is a placeholder until the lead wires the live Stripe payment links.",
        "plans": [
            {
                "id": "basic",
                "name": "Basic",
                "price_monthly": 9,
                "description": "Real-time alerts with 5 trending products discovered daily.",
                "features": [
                    "Real-time trend signal alerts",
                    "5 trending products per day",
                    "Basic SEO content generation",
                ],
                "checkout_status": "coming-soon",
            },
            {
                "id": "pro",
                "name": "Pro",
                "price_monthly": 20,
                "description": "Unlimited trends, advanced affiliate content, and automation templates.",
                "features": [
                    "Unlimited trending products daily",
                    "Advanced affiliate + SEO content generation",
                    "Pinterest/Reddit automation templates",
                ],
                "checkout_status": "coming-soon",
            },
        ],
        "notes": [
            "The app does not call Stripe directly.",
            "Tier access is controlled by the database user record.",
            "Live checkout links will be added by the lead.",
        ],
    }


def get_process_health() -> Dict[str, str]:
    health = {
        "saas_server": "green",
        "blog_server": "red",
        "scheduler_daemon": "red",
    }

    try:
        response = httpx.get("http://localhost:5000/api/stats", timeout=1.0)
        if response.status_code == 200:
            health["blog_server"] = "green"
        else:
            health["blog_server"] = "yellow"
    except Exception:
        health["blog_server"] = "red"

    try:
        output = subprocess.check_output(["ps", "-ef"]).decode()
        health["scheduler_daemon"] = "green" if "scheduler.py" in output else "red"
    except Exception:
        health["scheduler_daemon"] = "red"

    return health


@router.get("/admin/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard():
    process_health = get_process_health()

    blog_stats: Dict[str, Any] = {"totalPosts": 0, "email": {"subscribers": 0}}
    subscribers_count = 0
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:5000/api/stats", timeout=1.0)
            if response.status_code == 200:
                blog_stats = response.json()
                subscribers_count = blog_stats.get("email", {}).get("subscribers", 0)
    except Exception:
        pass

    today = datetime.utcnow().strftime("%m-%d")
    alert_log: List[Dict[str, Any]] = [
        {
            "id": "baseline-1",
            "timestamp": datetime.utcnow().strftime("%m-%d %H:%M"),
            "type": "info",
            "message": "Command dashboard is reporting the current honest baseline. Live revenue remains $0 and unconnected metrics stay empty until verified data sources are wired.",
        }
    ]

    log_path = "/tmp/trendcatcher.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as handle:
                lines = handle.readlines()[-10:]
            for index, line in enumerate(reversed(lines)):
                if not line.strip():
                    continue
                alert_log.append(
                    {
                        "id": f"runtime-{index}",
                        "timestamp": datetime.utcnow().strftime("%m-%d %H:%M"),
                        "type": "info",
                        "message": line.strip()[:220],
                    }
                )
        except Exception:
            pass

    return {
        "revenue": {
            "total": 0.0,
            "saas_mrr": 0.0,
            "affiliate": 0.0,
            "currency": "USD",
        },
        "traffic": {
            "daily": 0,
            "weekly": 0,
            "monthly": 0,
            "history": [],
        },
        "trending_products_today": 0,
        "content_status": {
            "published": blog_stats.get("totalPosts", 0),
            "scheduled": 0,
        },
        "top_performing_posts": [],
        "subscribers": {
            "count": subscribers_count,
            "conversion_rate": "0.0%",
            "history": [{"date": today, "subs": subscribers_count}],
        },
        "process_health": process_health,
        "alert_log": alert_log[:15],
    }
