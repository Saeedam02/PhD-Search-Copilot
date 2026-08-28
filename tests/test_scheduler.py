import asyncio

import pytest

from phd_search_agent.scheduler import run_daemon


def test_daemon_rejects_nonpositive_interval():
    async def cycle():
        return None

    with pytest.raises(ValueError):
        asyncio.run(run_daemon(cycle, 0))
