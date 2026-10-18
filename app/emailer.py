"""Email notifications for new inquiries.

Three modes, picked by environment (in order):
1. RESEND_API_KEY set  -> Resend HTTPS API (works on hosts like Render free
   tier where outbound SMTP ports are blocked).
2. SMTP_HOST set        -> plain SMTP (VPS / paid hosts).
3. Neither set          -> notification is logged, inquiry still saved.

A failed send never fails the inquiry request itself — the inquiry is always
saved to the database first.
"""

import json
import logging
import smtplib
import urllib.request
from email.message import EmailMessage

from .config import settings
from .models import Inquiry

log = logging.getLogger("rizz_studio.email")


def _body(inquiry: Inquiry) -> str:
    return (
        f"New project inquiry for Rizz Edits Studio\n"
        f"----------------------------------------\n"
        f"Name:    {inquiry.name}\n"
        f"Email:   {inquiry.email}\n"
        f"Service: {inquiry.service}\n"
        f"Page:    {inquiry.source_page or '-'}\n"
        f"Time:    {inquiry.created_at}\n"
        f"\nMessage:\n{inquiry.message}\n"
    )


def _send_via_resend(inquiry: Inquiry) -> bool:
    payload = json.dumps(
        {
            "from": settings.RESEND_FROM or "Rizz Edits Studio <onboarding@resend.dev>",
            "to": [settings.NOTIFY_TO],
            "reply_to": inquiry.email,
            "subject": f"[Rizz Edits Studio] New inquiry: {inquiry.service} — {inquiry.name}",
            "text": _body(inquiry),
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status in (200, 201)


def _send_via_smtp(inquiry: Inquiry) -> bool:
    msg = EmailMessage()
    msg["Subject"] = f"[Rizz Edits Studio] New inquiry: {inquiry.service} — {inquiry.name}"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.NOTIFY_TO
    msg["Reply-To"] = inquiry.email
    msg.set_content(_body(inquiry))
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
    return True


def send_inquiry_notification(inquiry: Inquiry) -> str:
    """Returns 'sent', 'not_configured', or 'failed'."""
    if not settings.NOTIFY_TO:
        log.info("NOTIFY_TO not set; inquiry #%s logged instead of emailed.", inquiry.id)
        return "not_configured"
    try:
        if settings.RESEND_API_KEY:
            ok = _send_via_resend(inquiry)
        elif settings.SMTP_HOST:
            ok = _send_via_smtp(inquiry)
        else:
            log.info("No email provider configured; inquiry #%s logged.", inquiry.id)
            return "not_configured"
    except Exception as exc:  # never break the request on email failure
        log.warning("Failed to send inquiry notification email: %s", exc)
        return "failed"
    return "sent" if ok else "failed"
