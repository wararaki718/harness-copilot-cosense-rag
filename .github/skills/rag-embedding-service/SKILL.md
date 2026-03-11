---
name: rag-embedding-service
description: Guide for implementing and operating the Japanese-SPLADE embedding API used by ingestion and retrieval flows.
---

# RAG Embedding Service

This skill helps you implement and maintain the shared embedding service for document and query vectorization.

## When to use this skill

Use this skill when you need to:
- Implement or change `POST /embed` request/response handling
- Keep document/query preprocessing consistent
- Improve embedding throughput with batch inference
- Handle embedding timeout/retry/failure behavior safely

## Service contract

- Endpoint: `POST /embed`
- Request: `{ "texts": ["..."], "type": "document|query" }`
- Response: `{ "vectors": [[...], [...]] }`

## Implementation workflow

1. Confirm model and preprocessing compatibility assumptions
2. Validate payload shape and input limits
3. Execute embedding with predictable batching strategy
4. Return stable response schema with ordered vector outputs
5. Surface failure paths with retry-aware handling and logs

## Quality checklist

- Document/query paths apply equivalent preprocessing policy
- Response shape is stable and backward compatible
- Timeouts and transient failures are handled explicitly
- Throughput tuning does not change semantic output unexpectedly

## Best practices

- Keep API behavior deterministic and observable
- Isolate model-specific logic from transport/interface code
- Version any contract-affecting changes clearly
- Coordinate schema-impacting changes with retrieval/indexing owners
