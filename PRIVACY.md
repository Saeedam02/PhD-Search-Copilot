# Privacy

This repository is designed to be **local-first**.

## Never commit private application data

Real candidate data should live under `workspace/`, which is ignored by Git.
That includes:

- CV/resume;
- transcript;
- thesis drafts;
- unpublished papers;
- recommendation letters;
- addresses and phone numbers;
- personal email addresses;
- application IDs;
- offer/rejection correspondence;
- private professor correspondence;
- authentication tokens and API keys.

## Model/API data

Live agent runs send the task context needed for that run to the configured OpenAI API. Before using this project, review the data-handling terms that apply to your OpenAI account and organization.

The agent should be given the minimum candidate evidence needed to do its job. Do not place passports, national IDs, banking details, or unrelated sensitive documents in the ingestion folder.

## Search evidence

Search/verification results can contain public contact details and public academic information. Store only what is necessary for the application workflow.

## Tracing

The OpenAI Agents SDK supports tracing. If your organization does not want run traces, set:

```text
OPENAI_AGENTS_DISABLE_TRACING=1
```

## Git history warning

Adding a file to `.gitignore` does not remove a secret that was already committed. If you accidentally commit a key or sensitive document, rotate/revoke the credential where relevant and rewrite Git history before treating the repository as safe.
