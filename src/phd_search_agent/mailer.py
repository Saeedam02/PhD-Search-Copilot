"""Explicit post-approval SMTP dispatch adapter.

This module is intentionally separate from the autonomous orchestrator. An
approved item still requires the user to invoke a dispatch command.
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_FROM"))


def send_email(*, to: str, subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST")
    from_addr = os.getenv("SMTP_FROM")
    if not host or not from_addr:
        raise RuntimeError("SMTP_HOST and SMTP_FROM must be configured")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = os.getenv("SMTP_USE_TLS", "true").casefold() in {"1", "true", "yes", "on"}

    message = EmailMessage()
    message["From"] = from_addr
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(message)
