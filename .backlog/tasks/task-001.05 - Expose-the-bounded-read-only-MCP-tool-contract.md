---
id: TASK-001.05
title: Expose the bounded read-only MCP tool contract
status: To Do
assignee: []
created_date: '2026-08-20 17:04'
labels:
  - mcp
  - tools
dependencies:
  - TASK-001.04
references:
  - 'https://github.com/modelcontextprotocol/python-sdk'
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose the approved read-only ILIAS capabilities to local MCP clients over stdio with stable English schemas, bounded results, provenance, trust metadata, and actionable errors. The tool layer must remain independent of Stuttgart HTML details.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The server exposes authentication status, course listing and details, learning-object traversal and details, upcoming items, dashboard context, controlled download, local extraction, and cache refresh tools.
- [ ] #2 Every tool documents fields, defaults, bounds, freshness, side effects, and error behavior in English.
- [ ] #3 List results use opaque cursor pagination and dashboard results report truncation explicitly.
- [ ] #4 Auth, permission, availability, rate, compatibility, content, extraction, cursor, and argument failures map to stable error codes.
- [ ] #5 Subprocess tests prove stdout contains only MCP protocol traffic while integration tests exercise every tool through the fake instance.
<!-- AC:END -->
