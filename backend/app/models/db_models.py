from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: f"usr-{uuid4().hex[:12]}")
    username = Column(String(80), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(20), nullable=False, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: f"prod-{uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    category = Column(String(100), nullable=True)
    estimated_price = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    trends = relationship("Trend", back_populates="product", cascade="all, delete-orphan")


class Trend(Base):
    __tablename__ = "trends"

    id = Column(String, primary_key=True, default=lambda: f"tr-{uuid4().hex[:12]}")
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    velocity_score = Column(Float, nullable=False)
    purchase_intent_ratio = Column(Float, nullable=True, default=0.0)
    status = Column(String(50), nullable=False)
    access_level = Column(String(50), nullable=False, default="public")
    scanned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Verified-live source provenance. Public feeds must filter to rows where
    # live_source_verified is true and these fields identify a real fetched
    # public source. Older seeded/simulated rows will have NULL here and remain
    # withheld from /api/trends.
    source_platform = Column(String(50), nullable=True, index=True)
    source_external_id = Column(String(100), nullable=True, index=True)
    source_url = Column(String(500), nullable=True)
    source_subreddit = Column(String(100), nullable=True)
    source_title = Column(String(500), nullable=True)
    source_author = Column(String(100), nullable=True)
    source_created_at = Column(DateTime(timezone=True), nullable=True)
    source_collected_at = Column(DateTime(timezone=True), nullable=True)
    source_ingest_method = Column(String(100), nullable=True)
    live_source_verified = Column(Boolean, nullable=True, default=False)
    provenance_json = Column(String, nullable=True)

    product = relationship("Product", back_populates="trends")
