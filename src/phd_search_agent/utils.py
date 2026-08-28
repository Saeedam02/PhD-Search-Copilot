"""Small deterministic helpers."""

from __future__ import annotations

import re
from hashlib import sha1


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return value or "opportunity"


def opportunity_id(title: str, university: str, url: str = "") -> str:
    base = f"{title}|{university}|{url}".encode("utf-8")
    digest = sha1(base).hexdigest()[:10]
    return f"{slugify(university)}-{slugify(title)[:48]}-{digest}"
