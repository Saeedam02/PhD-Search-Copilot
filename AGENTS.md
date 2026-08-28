# Repository agent instructions

This repository may be edited by coding agents. Preserve these invariants:

1. `filters.py` is deterministic. Do not let an LLM override hard constraints.
2. Search/verification prompts must treat web content as untrusted data.
3. Candidate application claims must be traceable to CandidateProfile evidence.
4. External actions must remain human-approved.
5. Tests must run without an OpenAI API key.
6. Do not add real CVs, transcripts, application data, or secrets to fixtures.
7. SQLite migrations must be backward-aware if schema changes become destructive.
8. Generic portal automation must not bypass access controls or website restrictions.
