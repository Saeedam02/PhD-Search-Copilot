"""Simple long-running scheduler without an extra background-worker dependency."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


async def run_daemon(
    cycle: Callable[[], Awaitable[object]],
    interval_hours: float,
    *,
    run_immediately: bool = True,
) -> None:
    if interval_hours <= 0:
        raise ValueError("interval_hours must be positive")
    if run_immediately:
        await cycle()
    seconds = interval_hours * 3600
    while True:
        await asyncio.sleep(seconds)
        await cycle()
