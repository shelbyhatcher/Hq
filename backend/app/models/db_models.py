from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Float, ForeignKey, func
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

    product = relationship("Product", back_populates="trends")
