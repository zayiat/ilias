---
id: TASK-001.01
title: Establish the safe ILIAS MCP foundation
status: In Progress
assignee:
  - Eren
created_date: '2026-08-20 17:03'
updated_date: '2026-08-21 13:47'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement only the foundation scope defined for TASK-001.01, corresponding to Tasks 1 and 2 of docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md.

1. Verify the task branch/workspace baseline and tool availability.
2. Establish the Python 3.12 uv project, locked dependencies, package metadata, pytest, Ruff, and mypy configuration.
3. Use strict Red-Green-Refactor cycles to define and implement immutable normalized domain identities and values, bounded pagination, provenance/trust metadata, artifact validation, and stable failures.
4. Use strict Red-Green-Refactor cycles to implement validated non-secret TOML/environment configuration with safe URLs and bounded cache/request/artifact/result settings.
5. Use strict Red-Green-Refactor cycles to implement structured stderr-only operational logging with conservative redaction of credentials, sessions, sensitive URL parameters, and authored content.
6. Run focused tests throughout, then the complete non-live suite, formatting, linting, type checks, dependency lock verification, and diff hygiene.
7. Obtain task-scoped and final branch reviews; resolve all Critical and Important findings.
8. Record modified files, objective acceptance-criteria evidence, implementation notes, and final summary in Backlog; mark Done only after reading the finalization guide.
9. Commit in English without automated authorship, push task-001.01, and create a pull request against main.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Execution started on branch `task-001.01`. The user declined an additional linked worktree. Python 3.12.12 was found in the existing uv-managed toolchain; uv 0.12.5 was installed in an isolated temporary bootstrap environment after the managed interpreter correctly rejected direct package installation. Superpowers SDD scope is limited to Plan Tasks 1 and 2.

Plan Task 1 completed in commit d9ec22b. Added the locked Python 3.12 package foundation, immutable Pydantic domain values, opaque pagination, and stable error taxonomy. Verification: 18 focused/full tests passed; Ruff lint/format, mypy, uv lock check, and diff check passed. The Task 1 execution report is local at .superpowers/sdd/2026-08-20-ilias-mcp-server-mvp/task-1-report.md.

Plan Task 1 review fix round 1 completed in commit c325d80. The domain is now protocol/filesystem-neutral, requires offset-aware timestamps without tzdata, enforces provenance-instance cohesion, and has complete stable-error coverage. Fresh verification: 30 focused/full tests passed; Ruff lint/format, mypy, uv lock check, and diff check passed. Full evidence is appended to the local Task 1 report.
<!-- SECTION:NOTES:END -->
