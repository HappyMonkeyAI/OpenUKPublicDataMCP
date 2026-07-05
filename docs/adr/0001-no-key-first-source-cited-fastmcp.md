# ADR 0001 — No-key-first, source-cited FastMCP server

## Status

Accepted

## Context

The project was inspired by broad public-data MCP gateways such as allemannsdata.com and existing UK-specific MCP attempts. UK public data is fragmented across GOV.UK, data.gov.uk, Parliament, ONS, local/sector bodies, and optional-key APIs.

A useful product should work immediately for agents without signup while still allowing richer authenticated sources later.

## Decision

OpenUKPublicDataMCP will be a Python FastMCP server with:

- no-key core tools
- optional-key provider modules
- a source registry describing auth, licence, official status, docs, and coverage
- source metadata in every tool response
- stdio-safe runtime defaults

## Consequences

- Core scope excludes useful sources that require credentials until optional modules exist.
- Tool design focuses on common user questions, not exhaustive upstream endpoint mirroring.
- More metadata is returned per call, but agents can cite and reason about freshness/auth/licence.
