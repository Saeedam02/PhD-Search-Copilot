# OpenAI runtime

The live implementation uses the OpenAI Agents SDK for Python (`openai-agents`).

As of the v2.0.0 release, the repository targets `openai-agents>=0.22.0,<0.23` and Python 3.10+.

Relevant official documentation:

- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/quickstart/
- https://openai.github.io/openai-agents-python/tools/
- https://openai.github.io/openai-agents-python/human_in_the_loop/
- https://openai.github.io/openai-agents-python/tracing/

The SDK uses the Responses API by default for OpenAI models and supports hosted web search, structured outputs, agent orchestration, tracing, and approval patterns.

## Why use the Agents SDK here?

The project has long-running, coordinated stages and benefits from typed agent outputs and hosted web search. The application still owns persistence, hard rules, and approval state so the workflow remains auditable even when a run finishes or restarts.

## Tracing

Tracing is useful when debugging discovery/verification behavior. To disable it:

```bash
export OPENAI_AGENTS_DISABLE_TRACING=1
```

## Model selection

Set:

```text
OPENAI_MODEL=gpt-5.6-sol
```

or another compatible OpenAI model available to your API account. The model is configuration, not hard-coded workflow logic.
