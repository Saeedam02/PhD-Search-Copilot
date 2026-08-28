# Contributing

Contributions are welcome.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
pytest --cov=phd_search_agent --cov-branch
```

## Design rules

1. Deterministic hard constraints must remain outside the LLM.
2. Never label an inferred fact as verified.
3. External send/submit/pay/withdraw/accept actions must require explicit approval.
4. New agent behavior needs tests around the deterministic boundary.
5. Do not include real candidate files in fixtures.
6. Prefer official university/funder evidence for verification.
7. Avoid implementing portal automation that violates website terms or bypasses access controls.

## Pull requests

Explain:

- the user problem;
- the design change;
- tests added or updated;
- privacy/security implications;
- any new external service requirements.
