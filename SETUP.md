# Detailed setup

## 1. Clone and install

```bash
git clone https://github.com/Saeedam02/phd-search-copilot.git
cd phd-search-copilot
python -m venv .venv
```

Activate the environment and install:

```bash
python -m pip install -e ".[dev]"
```

## 2. Initialize private state

```bash
phd-agent init
```

## 3. Configure API access

Copy `.env.example` to `.env` and provide `OPENAI_API_KEY`. `.env` is ignored by Git.

## 4. Add candidate files

Put only relevant candidate evidence under `workspace/private/`. Text PDFs, DOCX, Markdown, and text are supported.

## 5. Ingest and review

```bash
phd-agent ingest
```

Open `workspace/config/candidate.yaml` and correct extraction errors before autonomous application drafting.

## 6. Define target positions

Edit `workspace/config/search_preferences.yaml`. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## 7. Validate without API use

```bash
phd-agent validate
```

## 8. Run the agent

```bash
phd-agent run-cycle
```

## 9. Review results

```bash
phd-agent status
phd-agent deadlines --within 30
phd-agent approvals
phd-agent dashboard
```

## 10. Enable recurring operation

```bash
phd-agent daemon
```

or use the OS scheduler instructions in `docs/AUTOMATION.md`.
