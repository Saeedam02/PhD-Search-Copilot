# Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
phd-agent init
```

Then:

1. Put your CV/supporting files in `workspace/private/`.
2. Set `OPENAI_API_KEY` in `.env` or your shell.
3. Edit `workspace/config/search_preferences.yaml`.
4. Run `phd-agent ingest`.
5. Review `workspace/config/candidate.yaml`.
6. Run `phd-agent run-cycle`.
7. Open `workspace/reports/dashboard.html` after `phd-agent dashboard`.
8. Review any queued application/outreach actions with `phd-agent approvals`.
