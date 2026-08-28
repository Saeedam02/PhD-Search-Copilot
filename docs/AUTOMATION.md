# Automation

## Foreground daemon

```bash
phd-agent daemon
```

The daemon uses the interval configured in `workspace/config/search_preferences.yaml`.

## Linux cron

Run once per day at 08:00:

```cron
0 8 * * * cd /path/to/phd-search-copilot && /path/to/.venv/bin/phd-agent run-cycle >> workspace/state/cron.log 2>&1
```

## systemd

For a long-running host, prefer a systemd service/timer so logs and restarts are managed by the OS.

## Windows Task Scheduler

Create a task that runs:

```text
C:\path\to\.venv\Scripts\phd-agent.exe run-cycle
```

with the repository as the working directory.

## GitHub Actions scheduling

Possible, but not enabled by default because it requires storing an API key as a GitHub Actions secret and can consume API usage unattended. A template is provided under `automation/github-actions-daily.yml.example`.

Do not use a public repository secret to store CV content. Candidate data should remain in a private/local workspace or be provisioned through a secure store you control.
