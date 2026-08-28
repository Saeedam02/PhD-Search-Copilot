# Validation status

Validated locally on Python 3.13.5 for the deterministic/offline core.

```text
77 tests passed
branch-aware coverage: 93.05%
configured minimum coverage: 88%
```

Validated areas include:

- funding, stipend, tuition, location, deadline, topic, method, GRE, fee, position-type, start-date, language, and custom hard filters;
- weighted scoring and priority bands;
- persistent SQLite opportunity/approval/outcome storage;
- state-machine transitions;
- document extraction for text/Markdown/DOCX;
- application/supervisor/interview artifacts;
- approval creation and decisions;
- SMTP adapter preconditions and TLS/login behavior using mocks;
- dashboard generation;
- deadline analytics and outcome statistics;
- end-to-end orchestration with a fake agent runtime;
- prevention of duplicate approvals on repeated autonomous cycles.

## Not executed in this validation environment

A live OpenAI API/WebSearchTool run was not executed because the build environment had no API key/network package installation. The live runtime is isolated behind `AgentRuntime`, and CI tests deliberately do not require an API key.

Before production use, run one live cycle on your machine and inspect the OpenAI trace plus generated evidence records.
