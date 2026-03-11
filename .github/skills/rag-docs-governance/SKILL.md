---
name: rag-docs-governance
description: Guide for maintaining architecture/API documentation consistency and Mermaid-based flow explanations across this project.
---

# RAG Documentation Governance

This skill helps you keep project documentation accurate, traceable, and aligned with implementation and operational behavior.

## When to use this skill

Use this skill when you need to:
- Update architecture or flow descriptions after implementation changes
- Add or revise API contracts and response examples
- Keep README and component responsibilities in sync
- Produce diagrams for architecture/workflow explanations

## Required references

- Architecture source of truth: [architecture.md](../../../architecture.md)
- Copilot project rules: [copilot-instructions.md](../../copilot-instructions.md)
- Shared engineering rules: [agents.instructions.md](../../instructions/agents.instructions.md)

## Required constraints

- Prefer Mermaid for architecture and flow diagrams
- Keep terminology consistent (`sparse vector`, `Top-K`, `citation`)
- Avoid stale docs after behavior/schema changes
- Include impact and minimal verification steps in documentation updates

## Documentation workflow

1. Identify implemented behavior and changed scope
2. Update affected doc sections with precise wording
3. Add or revise examples (request/response/data schema)
4. Verify links and terms are consistent across docs

## Best practices

- Write in active voice and keep statements testable
- Distinguish assumptions from implemented behavior
- Document fallback and failure modes, not only happy paths
- Keep examples minimal but realistic
