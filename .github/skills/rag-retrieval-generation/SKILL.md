---
name: rag-retrieval-generation
description: Guide for implementing query embedding, Top-K sparse retrieval, grounded prompting, and citation-preserving answer generation.
---

# RAG Retrieval & Generation

This skill helps you build and tune the online question-answering path from query intake to grounded response output.

## When to use this skill

Use this skill when you need to:
- Implement or modify `/search` behavior
- Tune Top-K, threshold, and retrieval quality controls
- Build prompt context from retrieved documents
- Integrate or adjust Ollama Gemma3 generation behavior

## Online flow

1. Receive query from frontend
2. Embed query through Embedding API
3. Run sparse-vector search in Elasticsearch
4. Build prompt with retrieved context
5. Generate answer with Ollama Gemma3
6. Return `answer` and `citations`

## Required constraints

- Prioritize retrieved context over model prior knowledge
- Preserve citation traceability (`title`, `url`) in response
- Keep low-relevance fallback behavior for information insufficiency
- Handle timeout/token-limit/retry for generation calls

## Quality checklist

- Search parameters are configurable (Top-K, threshold)
- Empty/low-score retrieval path returns explicit fallback response
- Response schema remains backward compatible
- No fabricated citation entries are introduced

## Best practices

- Keep retrieval logic and generation logic separated by clear boundaries
- Validate all external API payloads and sanitize prompt inputs
- Prefer deterministic prompt templates for reproducibility
- Document ranking or schema changes with impact notes
