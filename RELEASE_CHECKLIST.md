# Release checklist

- [ ] `ruff check .`
- [ ] `pytest --cov=phd_search_agent --cov-branch`
- [ ] Confirm no real CV/application data is tracked.
- [ ] Confirm `.env` is not tracked.
- [ ] Review README examples for current CLI behavior.
- [ ] Review OpenAI Agents SDK dependency/API compatibility.
- [ ] Update `CHANGELOG.md`.
- [ ] Update version in `pyproject.toml`, package `__init__.py`, and `CITATION.cff`.
- [ ] Create Git tag/release.
