---
name: rag-frontend-experience
description: Guide for implementing React + TypeScript QA UI with clear states, citation display, and resilient error/retry UX.
---

# RAG Frontend Experience

This skill helps you implement and maintain the user-facing query and answer interface for this RAG application.

## When to use this skill

Use this skill when you need to:
- Build or update query input and answer display flows
- Improve loading, success, and error state management
- Ensure citations are visible and navigable in the UI
- Keep API type contracts consistent in TypeScript

## UI state model

Handle at least these states explicitly:
- Idle (before query)
- Loading (search/generation in progress)
- Success (answer + citations)
- Error (recoverable with retry)

## Required constraints

- Always show citation information alongside generated answers
- Keep retry path available when external calls fail
- Avoid ambiguous state transitions
- Maintain strict request/response typing

## Quality checklist

- User can distinguish processing vs completion instantly
- Error copy and actions help user recover without reload
- Citation links are visible and usable
- API failures do not crash the page state

## Best practices

- Centralize API models and error handling utilities
- Keep presentational components separate from data-fetch logic
- Prefer minimal, predictable UX over hidden automation
- Align terminology with architecture docs (sparse vector, Top-K, citation)
