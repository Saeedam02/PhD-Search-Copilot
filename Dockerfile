FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir .
COPY config ./config
COPY docs ./docs
COPY workspace/README.md ./workspace/README.md

CMD ["phd-agent", "daemon"]
