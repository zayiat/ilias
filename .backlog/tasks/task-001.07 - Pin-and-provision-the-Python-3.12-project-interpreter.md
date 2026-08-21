---
id: TASK-001.07
title: Pin and provision the Python 3.12 project interpreter
status: In Progress
assignee:
  - '@Eren'
created_date: '2026-08-21 17:08'
updated_date: '2026-08-21 17:08'
labels:
  - python
  - tooling
dependencies: []
parent_task_id: TASK-001
priority: high
type: bug
ordinal: 3600
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Restore a deterministic local development interpreter for the ILIAS MCP project. The repository currently declares Python 3.12 tooling expectations, but uv cannot find Python 3.12 and falls back to Python 3.13, leaving editor and command execution dependent on ambient machine state.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The repository selects Python 3.12 deterministically for uv-based development environments.
- [ ] #2 A fresh project virtual environment reports Python 3.12.
- [ ] #3 The locked test suite, formatting check, lint check, and type check pass with the selected interpreter.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve the reproduced RED signal that `uv python find 3.12` cannot locate the required interpreter.
2. Add the repository-level uv Python version pin for Python 3.12.
3. Provision Python 3.12 with uv and rebuild the ignored project virtual environment from the lockfile.
4. Verify the interpreter version, complete pytest suite, Ruff formatting and lint checks, mypy, lock consistency, and git diff hygiene.
5. Record objective evidence and finalize the Backlog task.
<!-- SECTION:PLAN:END -->
