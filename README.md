# PhD Search Copilot — Autonomous AI Agent

> Upload your academic profile once. Define the PhD you want. Let an AI agent continuously discover, verify, rank, research, and prepare the strongest opportunities — while keeping human approval before any external action.

[![CI](https://github.com/Saeedam02/phd-search-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/Saeedam02/phd-search-copilot/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Human approval](https://img.shields.io/badge/external_actions-human_approval_required-orange)

## What this is

PhD Search Copilot is a local-first, ChatGPT/OpenAI-powered **agentic workflow** for academic PhD discovery and applications. It is not a generic job scraper and it does not equate keyword overlap with admission probability.

The agent separates four things that are often mixed together:

1. **Hard eligibility and preference constraints** — funding, location, deadline, degree/language requirements, fees, GRE, and other deal-breakers.
2. **Evidence verification** — official vacancy pages and other authoritative sources are used to verify claims before the agent treats them as facts.
3. **Semantic fit** — research topics, methods, supervisor alignment, candidate skills, and competitiveness are scored only after hard constraints are considered.
4. **Human authorization** — the agent can prepare outreach and application artifacts autonomously, but sending emails, submitting applications, paying fees, withdrawing, or accepting offers requires explicit human approval.

## Agent workflow

```text
CV / thesis / transcript / papers / GitHub notes
                    │
                    ▼
              Profile Agent
                    │
                    ▼
             Candidate Memory
                    │
           ┌────────┴────────┐
           ▼                 ▼
    Search Preferences   Schedule
           │                 │
           └────────┬────────┘
                    ▼
             Discovery Agent
                    │
                    ▼
            Verification Agent
                    │
                    ▼
              Hard Filters
                    │
                    ▼
                Fit Agent
                    │
                    ▼
              Ranking Engine
                    │
            ┌───────┴────────┐
            ▼                ▼
    Supervisor Agent      Lab/Paper Research
            │                │
            └───────┬────────┘
                    ▼
           Application Agent
                    │
                    ▼
            Independent QA Agent
                    │
                    ▼
             Approval Queue
                    │
              HUMAN APPROVAL
                    │
                    ▼
            Send / Submit / Track
                    │
                    ▼
              Outcome Memory
```

The orchestration is deliberately **manager-style and deterministic**: Python controls the sequence, while specialized agents perform tasks where language/research reasoning is useful. This makes the workflow auditable and easier to test than one unconstrained autonomous prompt.

## Core features

- **Private academic profile ingestion** from PDF, DOCX, Markdown, and text files.
- **Funding constraints**: fully funded only, tuition waiver, stipend, minimum stipend, funding duration.
- **Location constraints**: required/preferred/excluded countries and cities.
- **Deadline constraints**: earliest/latest deadlines and minimum days remaining.
- **Research constraints**: required, preferred, and excluded topics/methods.
- **Application constraints**: GRE, fees, language requirements, named supervisor, position type, and custom deal-breakers.
- **Autonomous web discovery** through OpenAI's hosted web-search tool.
- **Verification agent** that treats unverified web snippets as leads, not facts.
- **Research-fit scoring** with an explicit weighted model — not fake admission probabilities.
- **Supervisor intelligence** based on recent, relevant research evidence.
- **Application package generation**: outreach email, cover letter, SOP/motivation letter, research statement, and application-answer notes.
- **Independent QA** to catch fabricated claims, inconsistent dates, unsupported paper references, and generic language.
- **Human approval queue** before any sensitive external action.
- **SQLite history** for opportunities, status, approvals, runs, and outcomes.
- **Dashboard** for deadlines, scores, pipeline state, and approvals.
- **Scheduled cycles** for continuous discovery and deadline monitoring.
- **Interview packs** generated when an application reaches interview state.

## Important safety boundary

The agent is autonomous for **research, analysis, drafting, monitoring, and preparation**. It is intentionally not autonomous for irreversible or identity-bearing actions.

The following remain approval-gated:

- sending a professor/recruiter email;
- submitting an application;
- paying an application fee;
- making a legal declaration or attestation;
- withdrawing an application;
- accepting or rejecting an offer.

This is a design feature, not a missing capability.

## Requirements

- Python 3.10+
- An OpenAI API key for live agent runs
- Internet access for web discovery/verification
- Git for version control

The live runtime uses the **OpenAI Agents SDK**, which provides agent orchestration, tools, structured outputs, sessions/tracing, and human-in-the-loop patterns on top of the Responses API.

## Quick start

```bash
git clone https://github.com/Saeedam02/phd-search-copilot.git
cd phd-search-copilot

python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install:

```bash
python -m pip install -e ".[dev]"
```

Create local configuration:

```bash
phd-agent init
```

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-sol
```

Do **not** commit `.env`.

## 1. Add your CV and supporting files

Place private files under:

```text
workspace/private/
├── cv/
│   └── my_cv.pdf
├── transcript/
│   └── transcript.pdf
├── thesis/
│   └── thesis.pdf
├── publications/
│   └── paper_01.pdf
└── supporting/
    ├── research_statement.docx
    └── github_notes.md
```

`workspace/*` is ignored by Git by default.

Then run:

```bash
phd-agent ingest
```

The Profile Agent extracts only supported evidence and creates:

```text
workspace/config/candidate.yaml
```

Review this file. The system distinguishes between verified/user-provided facts and model inference; application generators are instructed to use only supported candidate claims.

## 2. Define the PhD you want

Edit:

```text
workspace/config/search_preferences.yaml
```

Example:

```yaml
funding:
  fully_funded_only: true
  tuition_waiver_required: true
  stipend_required: true
  minimum_stipend:
    amount: 2500
    currency: EUR
    period: month

locations:
  preferred_countries:
    - Netherlands
    - Germany
    - Switzerland
    - Sweden
  allowed_countries:
    - Netherlands
    - Germany
    - Switzerland
    - Sweden
    - Denmark
    - Norway
    - Finland
    - Canada
  excluded_countries: []

research:
  required_topics:
    - autonomous systems
    - control systems
  preferred_topics:
    - autonomous vehicles
    - robotics
    - model predictive control
    - control barrier functions
  excluded_topics: []

application:
  avoid_mandatory_gre: true
  maximum_application_fee: 0

deadlines:
  minimum_days_remaining: 14
  latest_deadline: 2027-12-31
```

Unknown funding does **not** silently become "fully funded". It remains unverified until evidence supports it.

## 3. Run one autonomous cycle

```bash
phd-agent run-cycle
```

A cycle performs:

```text
discover → verify → hard-filter → score → rank → supervisor research
         → optionally prepare application → QA → approval queue
```

By default, high-priority eligible opportunities are researched automatically. Application packages can also be auto-prepared when enabled in `automation` settings.

## 4. Inspect the pipeline

```bash
phd-agent status
phd-agent deadlines --within 30
phd-agent approvals
phd-agent analytics
phd-agent dashboard
```

After you accumulate real outcomes, `phd-agent learn` can generate a cautious, review-only targeting report. It never silently rewrites your ranking weights.

The dashboard is written to:

```text
workspace/reports/dashboard.html
```

## 5. Schedule recurring operation

For a foreground worker:

```bash
phd-agent daemon
```

The daemon sleeps until the next configured cycle and then repeats discovery, verification, ranking, and preparation.

For a server/VPS/desktop machine, use the OS scheduler or service manager described in [docs/AUTOMATION.md](docs/AUTOMATION.md).

## 6. Human approval

View pending actions:

```bash
phd-agent approvals
```

Approve a prepared action:

```bash
phd-agent approve APPROVAL_ID
```

Reject it:

```bash
phd-agent reject APPROVAL_ID --reason "I want to rewrite the opening paragraph"
```

Approval records are persistent. Approved email drafts may be dispatched only through an explicit separate command and only when SMTP is configured.

## Repository structure

```text
phd-search-copilot/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/ci.yml
├── config/
│   ├── candidate.example.yaml
│   ├── search_preferences.example.yaml
│   └── scoring.example.yaml
├── docs/
│   ├── AGENT_ARCHITECTURE.md
│   ├── AUTOMATION.md
│   ├── DATA_MODEL.md
│   ├── HUMAN_APPROVAL.md
│   ├── PRIVACY.md
│   ├── SCORING.md
│   └── WORKFLOW.md
├── examples/
│   └── opportunities/
├── prompts/
│   └── manual/
├── src/phd_search_agent/
│   ├── agent_prompts/
│   ├── agent_runtime.py
│   ├── approvals.py
│   ├── artifacts.py
│   ├── cli.py
│   ├── config.py
│   ├── database.py
│   ├── dashboard.py
│   ├── filters.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── profile_ingest.py
│   ├── scheduler.py
│   ├── scoring.py
│   └── state_machine.py
├── tests/
├── workspace/
│   └── README.md
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── PRIVACY.md
├── README.md
├── ROADMAP.md
├── SECURITY.md
├── pyproject.toml
└── requirements.txt
```

## Scoring philosophy

A high semantic score can never rescue a position that violates a confirmed hard constraint.

If the opportunity passes hard filters, the ranking engine uses a configurable weighted score:

$$
S = \frac{\sum_i w_i s_i}{\sum_i w_i}
$$

Typical dimensions are:

- research alignment;
- supervisor alignment;
- methodology alignment;
- candidate skills alignment;
- funding quality;
- location fit;
- deadline practicality;
- competitiveness;
- evidence quality.

`S` is a prioritization score. It is **not** an admission probability.

See [docs/SCORING.md](docs/SCORING.md).

## Why specialized agents?

The workflow uses specialists because different tasks have different failure modes:

- the **Discovery Agent** optimizes recall;
- the **Verification Agent** optimizes factual evidence;
- the **Fit Agent** compares candidate and project substance;
- the **Supervisor Agent** researches academic overlap;
- the **Application Agent** writes role-specific artifacts;
- the **QA Agent** is deliberately independent of the drafter;
- the **Interview Agent** turns verified research context into preparation material.

Python owns state transitions and hard rules. The model does not get to override a funding or deadline constraint simply because a position "looks exciting."

## Tests

```bash
ruff check .
pytest --cov=phd_search_agent --cov-branch --cov-report=term-missing
```

Tests do not require an API key. Live model/web behavior is kept behind an injectable runtime so the deterministic core can be validated offline.

## Privacy

Never commit your real CV, transcript, passport/ID, recommendation letters, addresses, phone numbers, private emails, or application records.

The entire `workspace/` is ignored except its README. See [PRIVACY.md](PRIVACY.md).

## Limitations

- Web discovery is not guaranteed to find every vacancy.
- Funding language varies substantially by country and institution.
- Some university portals block automated browsing or require JavaScript/login.
- A model-generated research-fit score is a prioritization aid, not an admissions forecast.
- PDF extraction works best on text PDFs; scanned images may require separate OCR.
- Generic application-portal submission is intentionally not implemented as an unsupervised action.
- Users remain responsible for checking official requirements and final application content.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT.
