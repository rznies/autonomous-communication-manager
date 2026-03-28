# Security Policy

## Supported Versions

This repository is still pre-1.0. Only the latest commit on `master` receives security fixes.

| Version | Supported |
| --- | --- |
| `0.1.x` | Yes |
| `< 0.1.0` | No |

## Reporting a Vulnerability

Do not open a public GitHub issue for a suspected security issue.

Use one of these private paths instead:

1. GitHub private vulnerability reporting for this repository, if enabled.
2. Direct private contact with the repository maintainer through the same channel used to grant repo access.

Include:

- a short description of the issue
- the affected file, endpoint, or workflow
- reproduction steps
- impact and any known workaround

### Response targets

- Initial acknowledgement: within 3 business days
- Triage decision: within 7 business days
- Status updates: at least weekly until resolved or declined

### Disclosure policy

- Please keep the report private until a fix ships or the maintainer confirms the issue is not actionable.
- If credentials may have leaked, rotate them immediately and note the exposure window in the report.

## Security baselines

- Production secrets must come from environment variables or a secret manager, never tracked files.
- `.env` is local-only. Use `.env.example` for templates.
- Mutating API routes should require `X-ACM-API-Key` in deployed environments.
- `/health/live` and `/health/ready` must pass before a release is considered healthy.
