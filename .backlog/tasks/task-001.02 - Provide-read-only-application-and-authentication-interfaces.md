---
id: TASK-001.02
title: Provide read-only application and authentication interfaces
status: To Do
assignee: []
created_date: '2026-08-20 17:03'
labels:
  - mcp
  - authentication
dependencies:
  - TASK-001.01
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose a normalized read-only application interface for courses, learning objects, upcoming items, dashboard context, and authorized file access. Add explicit local authentication lifecycle behavior so MCP tools can report session state but can never receive credentials or unexpectedly launch an interactive login.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A deterministic fake instance implementation exercises active-course defaults, bounded pagination, date windows, dashboard truncation, and stable failures.
- [ ] #2 Authentication supports explicit login and status commands while missing or expired sessions produce actionable authentication-required outcomes.
- [ ] #3 Passwords are not persisted by the project and session material is stored outside repository files through the operating-system credential facility.
- [ ] #4 Tests prove that MCP-facing operations cannot start a browser or expose session material.
<!-- AC:END -->
