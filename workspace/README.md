# Local workspace

Everything in this directory is ignored by Git except this file.

After `phd-agent init`, the local structure is approximately:

```text
workspace/
├── config/
│   ├── candidate.yaml
│   ├── search_preferences.yaml
│   └── scoring.yaml
├── private/
│   ├── cv/
│   ├── transcript/
│   ├── thesis/
│   ├── publications/
│   └── supporting/
├── applications/
├── reports/
├── approvals/
└── state/
    └── phd_agent.db
```

Do not remove the workspace ignore rule unless you deliberately want to version private data.
