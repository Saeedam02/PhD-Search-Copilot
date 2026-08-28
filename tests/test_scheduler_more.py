import asyncio

from phd_search_agent.scheduler import run_daemon


def test_daemon_runs_immediately_then_sleeps(monkeypatch):
    calls = []

    async def cycle():
        calls.append("cycle")

    async def fake_sleep(_seconds):
        raise RuntimeError("stop")

    monkeypatch.setattr("phd_search_agent.scheduler.asyncio.sleep", fake_sleep)
    try:
        asyncio.run(run_daemon(cycle, 1, run_immediately=True))
    except RuntimeError as exc:
        assert str(exc) == "stop"
    assert calls == ["cycle"]
