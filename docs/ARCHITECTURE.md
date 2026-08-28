# Architecture

```mermaid
flowchart TD
    A[Private candidate files] --> B[Profile Agent]
    B --> C[CandidateProfile]
    C --> D[Orchestrator]
    P[Search preferences] --> D
    S[Scheduler] --> D
    D --> E[Discovery Agent + Web Search]
    E --> F[Verification Agent + Web Search]
    F --> G[Deterministic Hard Filters]
    G --> H[Fit Agent]
    H --> I[Weighted Ranking]
    I --> J[Supervisor/Lab Research Agent]
    J --> K[Application Agent]
    K --> L[Independent QA Agent]
    L --> M[Persistent Approval Queue]
    M --> N{Human approval}
    N -->|approved| O[Explicit external action]
    N -->|rejected| K
    O --> Q[Outcome tracking]
    Q --> R[Analytics + Outcome Learning Agent]
    R --> D
```

## Boundary between AI and deterministic code

### LLM/agent tasks

- extract a structured profile from unstructured evidence;
- discover opportunities;
- verify web evidence;
- assess semantic fit;
- research supervisors/labs;
- draft applications;
- independently review applications;
- prepare interviews;
- analyze outcome patterns cautiously.

### Deterministic code

- funding/location/deadline/application hard constraints;
- weighted-score arithmetic;
- workflow state transitions;
- database persistence;
- approval status;
- deadline calculations;
- artifact paths;
- SMTP dispatch preconditions.

This split is intentional: the model can reason about ambiguous academic fit, but it cannot decide that a self-funded position satisfies `fully_funded_only: true`.
