"""Request/response schemas with strict server-side validation."""

import re
from typing import Optional

from pydantic import BaseModel, field_validator

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# Must stay in sync with the service <select> options on the website.
ALLOWED_SERVICES = [
    "AI Automation",
    "Video Editing",
    "Web Development",
    "AI Chatbots",
    "Python Automation",
    "Other",
]


class InquiryCreate(BaseModel):
    name: str
    email: str
    service: str
    message: str
    source_page: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not 2 <= len(v) <= 100:
            raise ValueError("Name must be between 2 and 100 characters.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) > 254 or not EMAIL_RE.match(v):
            raise ValueError("Please provide a valid email address.")
        return v

    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        v = v.strip()
        if v not in ALLOWED_SERVICES:
            raise ValueError(f"Service must be one of: {', '.join(ALLOWED_SERVICES)}.")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not 10 <= len(v) <= 5000:
            raise ValueError("Message must be between 10 and 5000 characters.")
        return v

    @field_validator("source_page")
    @classmethod
    def validate_source_page(cls, v: str) -> str:
        return v.strip()[:120]


class InquiryResponse(BaseModel):
    ok: bool = True
    id: int
    message: str = "Inquiry received. We'll get back to you soon."


class InquiryOut(BaseModel):
    id: int
    name: str
    email: str
    service: str
    message: str
    source_page: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}
