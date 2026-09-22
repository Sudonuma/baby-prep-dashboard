"""Email sending for password recovery.

Uses the Resend API when RESEND_API_KEY is set (works on any host; free tier
available at resend.com). Without a key — local development — the message is
printed to the server console so the whole flow stays testable.
"""
import json
import os
import urllib.request


def send_email(to: str, subject: str, html: str) -> bool:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print(f"[mail:dev-only] to={to} subject={subject}\n{html}")
        return False
    payload = json.dumps({
        "from": os.environ.get("MAIL_FROM", "Baby Prep <onboarding@resend.dev>"),
        "to": [to],
        "subject": subject,
        "html": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as exc:  # network/API errors shouldn't break the request
        print(f"[mail] send failed: {exc}")
        return False
