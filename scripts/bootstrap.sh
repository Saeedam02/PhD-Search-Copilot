#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
phd-agent init

echo "Setup complete. Add OPENAI_API_KEY and candidate files before running phd-agent ingest."
