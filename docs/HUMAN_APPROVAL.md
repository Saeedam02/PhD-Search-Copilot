# Human approval

## What is approval-gated?

Any action that represents the candidate externally or can create an irreversible consequence:

- send email;
- submit application;
- pay fee;
- sign declaration;
- withdraw application;
- accept/reject offer.

## What can be autonomous?

- web research;
- verification;
- scoring/ranking;
- document drafting;
- QA;
- deadline reminders;
- dashboard updates;
- interview preparation.

## Persistent approval queue

Approval records live in SQLite and include:

- action type;
- target opportunity;
- artifact path;
- payload preview;
- created time;
- status;
- decision time;
- rejection reason.

Approving a draft does not automatically perform every possible external action. Dispatch/submission adapters remain explicit, separately invoked steps.
