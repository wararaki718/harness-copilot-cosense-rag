---
name: rag-platform-observability
description: Guide for Docker-based local operation, GitHub Actions CI, and Sentry/structured logging observability for RAG services.
---

# RAG Platform & Observability

This skill helps you keep runtime environments reproducible and failures diagnosable across local, CI, and operational paths.

## When to use this skill

Use this skill when you need to:
- Update Docker or docker-compose service wiring
- Add or adjust CI workflows (lint/test/build)
- Improve error tracking and telemetry via Sentry
- Standardize logs and trace IDs across services

## Required constraints

- Keep Elasticsearch and Python client versions compatible
- Keep secrets in environment variables only
- Capture external API timeouts/failures in logs and monitoring
- Ensure CI checks remain deterministic and reproducible

## Validation workflow

1. Run local service startup path with consistent env assumptions
2. Confirm core checks in CI pipeline definition
3. Verify error paths emit actionable logs and monitoring events
4. Document any infra behavior changes in README/architecture as needed

## Quality checklist

- Failure reasons are observable without reproducing blindly
- Service config drift is minimized between local and CI
- No secret values are committed or logged
- Compatibility assumptions are explicit

## Best practices

- Prefer small, scoped infra changes with rollback-friendly diffs
- Add guardrails before optimization
- Keep incident signals concise and actionable
- Treat observability as a default requirement, not optional add-on
