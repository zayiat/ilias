---
id: TASK-001.07
title: Pin and provision the Python 3.12 project interpreter
status: Done
assignee:
  - '@Eren'
created_date: '2026-08-21 17:08'
updated_date: '2026-08-21 17:10'
labels:
  - python
  - tooling
dependencies: []
modified_files:
  - .python-version
  - >-
    .backlog/tasks/task-001.07 -
    Pin-and-provision-the-Python-3.12-project-interpreter.md
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
- [x] #1 The repository selects Python 3.12 deterministically for uv-based development environments.
- [x] #2 A fresh project virtual environment reports Python 3.12.
- [x] #3 The locked test suite, formatting check, lint check, and type check pass with the selected interpreter.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve the reproduced RED signal that `uv python find 3.12` cannot locate the required interpreter.
2. Add the repository-level uv Python version pin for Python 3.12.
3. Provision Python 3.12 with uv and rebuild the ignored project virtual environment from the lockfile.
4. Verify the interpreter version, complete pytest suite, Ruff formatting and lint checks, mypy, lock consistency, and git diff hygiene.
5. Record objective evidence and finalize the Backlog task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause: no Python 3.12 interpreter was installed or pinned, so uv selected ambient Python 3.13. Added a repository-level `.python-version` pin, installed uv-managed CPython 3.12.12, and rebuilt the ignored `.venv` from the lockfile.

Objective verification: `uv python find 3.12` resolved `.venv\Scripts\python.exe`; `uv run python` reported 3.12.12; `uv run pytest -q` passed 89 tests; Ruff lint passed; Ruff format check reported 19 files already formatted; mypy passed for 5 source files; `uv lock --check` and `git diff --check` passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Summary

- Pinned the repository's uv development interpreter to Python 3.12.
- Provisioned uv-managed CPython 3.12.12 and rebuilt the ignored project virtual environment from the lockfile.
- Removed dependence on the ambient Python 3.13 installation for project commands and editor interpreter selection.

## Verification

- `uv python find 3.12`
- `uv run python` — Python 3.12.12
- `uv run pytest -q` — 89 passed
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv lock --check`
- `git diff --check`

## Risk / follow-up

The uv-managed interpreter is installed per user account. Other developers must allow uv to provision Python 3.12 when first syncing the repository.
<!-- SECTION:FINAL_SUMMARY:END -->
