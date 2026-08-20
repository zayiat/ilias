---
id: TASK-001.01
title: Establish the safe ILIAS MCP foundation
status: To Do
assignee: []
created_date: '2026-08-20 17:03'
labels:
  - mcp
  - foundation
dependencies: []
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the executable Python project foundation and stable normalized language used by every later ILIAS capability. Include validated non-secret configuration and operational logging that cannot corrupt stdio protocol traffic or disclose sensitive values.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Namespaced instance and object identities, courses, learning objects, upcoming items, artifacts, pagination, provenance, and stable failures are validated through tests.
- [ ] #2 Configuration rejects unsafe instance URLs and out-of-range cache, request, artifact, and result settings.
- [ ] #3 Operational logs use stderr and automated tests prove that common credential, session, URL-token, and content values are redacted.
- [ ] #4 The locked Python 3.12 project passes its focused tests, formatting, linting, and type checks.
<!-- AC:END -->
