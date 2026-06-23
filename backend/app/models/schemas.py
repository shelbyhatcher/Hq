from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseSchema):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    estimated_price: Optional[float] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime


class SocialSignalBase(BaseSchema):
    product_id: str
    platform: str
    external_id: str
    post_url: str
    engagement_score: int
    comment_count: Optional[int] = 0
    velocity_score: Optional[float] = 0.0
    raw_data: Optional[str] = None


class SocialSignalCreate(SocialSignalBase):
    pass


class SocialSignal(SocialSignalBase):
    id: str
    collected_at: datetime


class TrendBase(BaseSchema):
    product_id: str
    velocity_score: float
    purchase_intent_ratio: Optional[float] = 0.0
    status: str
    access_level: str = "public"


class TrendCreate(TrendBase):
    pass


class Trend(TrendBase):
    id: str
    scanned_at: datetime
    locked: bool = False
    product: Optional[Product] = None
    source_platform: Optional[str] = None
    source_external_id: Optional[str] = None
    source_url: Optional[str] = None
    source_subreddit: Optional[str] = None
    source_title: Optional[str] = None
    source_author: Optional[str] = None
    source_created_at: Optional[datetime] = None
    source_collected_at: Optional[datetime] = None
    source_ingest_method: Optional[str] = None
    live_source_verified: bool = False
    provenance: Optional[Dict[str, Any]] = None


class GeneratedContentBase(BaseSchema):
    product_id: str
    content_type: str
    title: str
    body: str
    seo_keywords: Optional[str] = None
    affiliate_links: Optional[str] = None
    status: str


class GeneratedContentCreate(GeneratedContentBase):
    pass


class GeneratedContent(GeneratedContentBase):
    id: str
    created_at: datetime
    published_at: Optional[datetime] = None


class UserBase(BaseSchema):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseSchema):
    email: str
    password: str


class User(UserBase):
    id: str
    tier: str = "free"


class Token(BaseSchema):
    access_token: str
    token_type: str
    user: User


class SubscriptionPlan(BaseSchema):
    id: str
    name: str
    price_monthly: int
    description: str
    features: List[str]
    checkout_status: str
    checkout_url: Optional[str] = None


class SubscriptionOverview(BaseSchema):
    current_tier: str
    checkout_mode: str
    message: str
    plans: List[SubscriptionPlan]
    notes: List[str]
