from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func

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
