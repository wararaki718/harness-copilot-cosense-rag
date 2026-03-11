---
name: rag-ingestion-indexing
description: Guide for implementing and operating Cosense batch ingestion and sparse-vector indexing. Use this for offline ingestion, chunking, and Elasticsearch upsert work.
---

# RAG Ingestion & Indexing

This skill helps you design, implement, and validate the offline ingestion pipeline for this Cosense-based RAG system.

## When to use this skill

Use this skill when you need to:
- Implement or update Cosense data collection jobs
- Add preprocessing or chunking logic for documents
- Generate sparse vectors via Embedding API and persist to Elasticsearch
- Improve ingestion reliability with retry, timeout, and idempotent upsert behavior

## Inputs and outputs

- Input: Manual batch trigger, Cosense API responses
- Processing: Cleaning, chunking, metadata enrichment, vectorization request
- Output: Elasticsearch documents containing content, metadata, and `sparse_vector`

## Required workflow

1. Read [architecture.md](../../../architecture.md) sections for Batch Ingestion and workflow
2. Confirm shared rules in [agents.instructions.md](../../instructions/agents.instructions.md)
3. Keep document IDs deterministic and safe for re-run upserts
4. Apply retries/timeouts for Cosense and Embedding API calls
5. Persist structured logs with success/failure counts and elapsed time

## Quality checklist

- Chunk data is traceable back to source page and chunk index
- Metadata fields (`title`, `url`, `updated_at`) are preserved
- `sparse_vector` schema matches embedding model output assumptions
- Re-running batch does not create duplicate logical documents

## Best practices

- Prefer incremental ingestion based on `updated_at`
- Fail fast on malformed external payloads, but keep per-item failure isolation
- Surface external dependency failures clearly for operators
- Keep changes local and backward compatible whenever possible
