"""ORM models."""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from .database import Base


class Inquiry(Base):
    """One project inquiry submitted through the website contact forms."""

    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(254), nullable=False, index=True)
    service = Column(String(80), nullable=False)
    message = Column(Text, nullable=False)
    source_page = Column(String(120), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
