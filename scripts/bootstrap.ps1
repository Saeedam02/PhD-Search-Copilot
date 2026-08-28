$ErrorActionPreference = "Stop"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
phd-agent init

Write-Host "Setup complete. Add OPENAI_API_KEY and candidate files before running phd-agent ingest."
