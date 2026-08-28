# Operations guide

## Daily routine

```bash
phd-agent run-cycle
phd-agent deadlines --within 30
phd-agent approvals
phd-agent dashboard
```

## Weekly routine

```bash
phd-agent analytics
phd-agent learn
```

Review high-priority opportunities, unresolved verification items, application drafts, and any proposed targeting changes.

## Before sending outreach

1. Open the opportunity's `supervisor_report.json`.
2. Check the cited evidence yourself.
3. Review `outreach_email.md`.
4. Review `qa_report.json`.
5. Approve the email action.
6. Dispatch explicitly only after checking the recipient address.

## Before submission

1. Verify the official deadline and portal.
2. Check all mandatory fields and required attachments.
3. Review final PDF/layout versions if you converted Markdown to PDF.
4. Approve the `submit_application` queue item.
5. Submit manually or through a future explicitly supported portal adapter.
6. Record `set-status ... submitted` and later use `outcome`.
