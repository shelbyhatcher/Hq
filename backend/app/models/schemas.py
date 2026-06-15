from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

# Configure standard config across schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Product Schemas -----------------
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

# ----------------- Social Signal Schemas -----------------
class SocialSignalBase(BaseSchema):
    product_id: str
    platform: str # 'tiktok', 'pinterest', 'reddit'
    external_id: str
    post_url: str
    engagement_score: int
    comment_count: Optional[int] = 0
    velocity_score: Optional[float] = 0.0
    raw_data: Optional[str] = None # JSON string

class SocialSignalCreate(SocialSignalBase):
    pass

class SocialSignal(SocialSignalBase):
    id: str
    collected_at: datetime

# ----------------- Trend Schemas -----------------
class TrendBase(BaseSchema):
    product_id: str
    velocity_score: float
    purchase_intent_ratio: Optional[float] = 0.0
    status: str # 'emerging', 'viral', 'saturated'

class TrendCreate(TrendBase):
    pass

class Trend(TrendBase):
    id: str
    scanned_at: datetime
    product: Optional[Product] = None

# ----------------- Generated Content Schemas -----------------
class GeneratedContentBase(BaseSchema):
    product_id: str
    content_type: str # 'blog_post', 'video_script', 'social_ad'
    title: str
    body: str
    seo_keywords: Optional[str] = None
    affiliate_links: Optional[str] = None # JSON string mapping retailer -> link
    status: str # 'draft', 'published'

class GeneratedContentCreate(GeneratedContentBase):
    pass

class GeneratedContent(GeneratedContentBase):
    id: str
    created_at: datetime
    published_at: Optional[datetime] = None

# ----------------- User & Authentication Schemas -----------------
class UserBase(BaseSchema):
    username: str
    email: str
    tier: str = "free" # 'free', 'premium'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseSchema):
    email: str
    password: str

class User(UserBase):
    id: str

class Token(BaseSchema):
    access_token: str
    token_type: str
    user: User

