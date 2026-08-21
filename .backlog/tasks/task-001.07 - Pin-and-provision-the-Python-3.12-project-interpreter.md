---
id: TASK-001.07
title: Pin and provision the Python 3.12 project interpreter
status: To Do
assignee: []
created_date: '2026-08-21 17:08'
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
