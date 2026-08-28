# Agent architecture

## Design choice: deterministic orchestrator + specialized agents

The project does not give one model unrestricted control over the complete application pipeline. A Python orchestrator owns state, hard filters, thresholds, and approval gates. Agents are called for tasks where semantic reasoning is useful.

```text
Orchestrator
├── Profile Agent
├── Discovery Agent + WebSearchTool
├── Verification Agent + WebSearchTool
├── Fit Agent
├── Supervisor Research Agent + WebSearchTool
├── Application Agent
├── QA Agent
└── Interview Agent
```

This pattern gives four advantages:

1. hard rules are testable without an LLM;
2. every stage can be logged separately;
3. failures can be retried without repeating the entire workflow;
4. external actions remain behind a separate approval boundary.

## OpenAI integration

The live runtime uses the OpenAI Agents SDK and its Responses-based model runtime. Hosted web search is attached only to agents that need fresh external evidence. Structured Pydantic outputs are used where possible so downstream Python does not have to parse free-form prose.

## Prompt-injection boundary

Web pages are untrusted data. Agent instructions explicitly state that text retrieved from a vacancy/professor page cannot override system/application instructions or request tool use on its own authority.

## Manager-style orchestration

Handoffs are useful when the model should dynamically route a conversation. This project instead uses a manager-style workflow because the stages are known in advance and need deterministic auditability.

## Human-in-the-loop

OpenAI's Agents SDK supports tool-level approval interruptions. This repository additionally keeps its own persistent approval queue because applications may need to wait hours or days for a human decision, independent of one in-memory model run.
