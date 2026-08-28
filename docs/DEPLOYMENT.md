# Deployment

This project is designed to run locally, on a private workstation, or on a private server/VPS.

Recommended production pattern:

```text
private host
├── cloned repository
├── virtual environment
├── environment secrets
├── Git-ignored workspace
├── scheduled phd-agent run-cycle
└── backed-up SQLite database
```

For shared/multi-user deployment, add authentication and encrypt candidate storage before exposing any dashboard on a network.
