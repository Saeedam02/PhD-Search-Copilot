# Security Policy

## Secrets

Use environment variables or a local `.env` file that is ignored by Git. Never hard-code:

- OpenAI API keys;
- SMTP passwords;
- university portal credentials;
- OAuth refresh tokens;
- application IDs that should remain private.

## External actions

The project intentionally requires human approval before external identity-bearing or irreversible actions. If you add new adapters, preserve this rule.

## Web content is untrusted input

Vacancy pages, professor pages, and scraped text can contain misleading or malicious instructions. Agent prompts explicitly treat web content as data, not instructions. Tool/code authors should maintain that separation.

## Reporting

Please use GitHub's private security-advisory mechanism for vulnerabilities rather than posting secrets or exploit details in a public issue.
