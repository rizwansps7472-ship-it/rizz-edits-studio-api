"""Inquiry endpoints: public submit + key-protected admin list."""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..database import Base, engine, get_db
from ..emailer import send_inquiry_notification

router = APIRouter(prefix="/api", tags=["inquiries"])


@router.post("/inquiries", response_model=schemas.InquiryResponse, status_code=201)
def create_inquiry(payload: schemas.InquiryCreate, db: Session = Depends(get_db)):
    inquiry = models.Inquiry(
        name=payload.name,
        email=payload.email,
        service=payload.service,
        message=payload.message,
        source_page=payload.source_page,
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    # Best effort: a failed email never fails the saved inquiry.
    send_inquiry_notification(inquiry)
    return schemas.InquiryResponse(id=inquiry.id)


@router.get("/inquiries", response_model=list[schemas.InquiryOut])
def list_inquiries(
    x_api_key: str = Header(default="", alias="X-API-Key"),
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if not settings.ADMIN_API_KEY or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden.")
    rows = (
        db.query(models.Inquiry)
        .order_by(models.Inquiry.id.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [
        schemas.InquiryOut(
            id=r.id,
            name=r.name,
            email=r.email,
            service=r.service,
            message=r.message,
            source_page=r.source_page,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in rows
    ]


@router.get("/health")
def health():
    return {"ok": True, "service": settings.APP_NAME}
