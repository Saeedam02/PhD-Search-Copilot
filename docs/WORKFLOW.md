# Workflow

## Setup

1. Initialize workspace.
2. Add private candidate files.
3. Ingest them into a structured candidate profile.
4. Review/correct the profile.
5. Define funding, location, deadline, research, and application constraints.

## Autonomous cycle

For each cycle:

1. Discovery Agent searches for recent opportunities.
2. Duplicate opportunities are merged by URL/title/institution identity.
3. Verification Agent checks official evidence for funding, deadline, eligibility, and supervisor/project details.
4. Hard Filter Engine marks each opportunity PASS, FAIL, or REVIEW.
5. Fit Agent generates semantic 0–10 dimensions with rationales.
6. Deterministic Scoring Engine computes the weighted ranking score.
7. High-priority opportunities receive supervisor/lab research.
8. If enabled, very high-priority opportunities receive an application draft.
9. QA Agent independently reviews the draft.
10. If QA passes, a human approval item is created.
11. Dashboard and run log are updated.

## Outcome cycle

After submission/interview/rejection/offer, record the outcome. Historical data can later be used to recalibrate priorities, but the project deliberately avoids presenting a personalized heuristic as a universal admission-probability model.
