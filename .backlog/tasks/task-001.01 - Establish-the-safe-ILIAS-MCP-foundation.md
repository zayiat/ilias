---
id: TASK-001.01
title: Establish the safe ILIAS MCP foundation
status: Done
assignee:
  - Eren
created_date: '2026-08-20 17:03'
updated_date: '2026-08-21 14:46'
labels:
  - mcp
  - foundation
dependencies: []
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
modified_files:
  - .backlog/tasks/task-001.01 - Establish-the-safe-ILIAS-MCP-foundation.md
  - .env.example
  - pyproject.toml
  - src/ilias_mcp/__init__.py
  - src/ilias_mcp/config.py
  - src/ilias_mcp/domain.py
  - src/ilias_mcp/errors.py
  - src/ilias_mcp/logging.py
  - tests/unit/test_config.py
  - tests/unit/test_domain.py
  - tests/unit/test_errors.py
  - tests/unit/test_logging.py
  - uv.lock
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
- [x] #1 Namespaced instance and object identities, courses, learning objects, upcoming items, artifacts, pagination, provenance, and stable failures are validated through tests.
- [x] #2 Configuration rejects unsafe instance URLs and out-of-range cache, request, artifact, and result settings.
- [x] #3 Operational logs use stderr and automated tests prove that common credential, session, URL-token, and content values are redacted.
- [x] #4 The locked Python 3.12 project passes its focused tests, formatting, linting, and type checks.
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

10. Final review fix wave: add focused RED regressions for IDNA-canonical hostname safety, required bounded unknown-object raw types, and process-keyed canonical ObjectId pseudonyms; implement the minimal boundary fixes; run focused and full verification; record evidence in the final fix report; commit once.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Execution started on branch `task-001.01`. The user declined an additional linked worktree. Python 3.12.12 was found in the existing uv-managed toolchain; uv 0.12.5 was installed in an isolated temporary bootstrap environment after the managed interpreter correctly rejected direct package installation. Superpowers SDD scope is limited to Plan Tasks 1 and 2.

Plan Task 1 completed in commit d9ec22b. Added the locked Python 3.12 package foundation, immutable Pydantic domain values, opaque pagination, and stable error taxonomy. Verification: 18 focused/full tests passed; Ruff lint/format, mypy, uv lock check, and diff check passed. The Task 1 execution report is local at .superpowers/sdd/2026-08-20-ilias-mcp-server-mvp/task-1-report.md.

Plan Task 1 review fix round 1 completed in commit c325d80. The domain is now protocol/filesystem-neutral, requires offset-aware timestamps without tzdata, enforces provenance-instance cohesion, and has complete stable-error coverage. Fresh verification: 30 focused/full tests passed; Ruff lint/format, mypy, uv lock check, and diff check passed. Full evidence is appended to the local Task 1 report.

Plan Task 1 review fix round 2 completed in commit 7edd097. Added explicit coverage that a LearningObject primary ID from another instance is rejected while parent, course, and provenance remain on the configured instance. This was coverage completion: the existing validator passed the new test without production changes. Fresh verification: 19 focused domain tests and 31 full tests passed; Ruff lint/format, mypy, uv lock check, and diff check passed. Full evidence is appended to the local Task 1 report.

Plan Task 1 (Python package and domain contract) completed under TDD and passed task-scoped spec/quality review after two fix rounds. Review corrections removed HTTP/filesystem/CLI coupling from the domain, removed the extra tzdata dependency, enforced cross-instance identity cohesion, and expanded stable-error and timestamp validation coverage. Final Task 1 evidence: 31 tests passed plus Ruff, format, mypy, and uv lock checks.

Final review fix wave started. Root-cause review confirmed three boundary issues: hostname safety checks run before IDNA canonicalization; LearningObject does not conditionally require raw_instance_type for unknown objects; logging validates but hashes the unparsed input with unsalted SHA-256. Scope remains limited to Plan Tasks 1-2.

Final review fix wave completed in commit `80ec1a3` (`Harden identity canonicalization boundaries`). Strict TDD evidence: focused RED was 13 failed / 64 passed for the expected missing behaviors; focused GREEN was 77 passed. Fresh final verification: focused 77 passed, full 89 passed, Ruff check passed, Ruff format check reported 18 files formatted, mypy passed for 5 source files, uv lock check resolved 18 packages, and git diff check passed. The full local report is `.superpowers/sdd/2026-08-20-ilias-mcp-server-mvp/final-fix-report.md`; `progress.md` was not edited.

Final whole-branch review completed. The reviewer approved both controller rulings: conservative bounded numeric defaults and trusted operator-selected non-root artifact directories. A final fix wave closed Unicode/IDNA local-host aliases, required bounded raw types for unknown learning objects, and replaced enumerable object-ID hashes with canonical process-scoped HMAC pseudonyms. Scoped re-review found all Critical/Important findings addressed and declared the branch ready to merge. One non-blocking Minor remains: a test comparing keyed and unkeyed digest strings is partly guaranteed by their prefixes; production behavior and other HMAC tests remain valid.

Objective finalization evidence on commit 366d3fa: `uv sync --locked` resolved/checked 18 packages; `uv run pytest -v` passed 89/89 tests on Python 3.12.12; `uv run ruff check .` passed; `uv run ruff format --check .` reported 18 files formatted; `uv run mypy src` reported no issues in 5 source files; `uv lock --check` passed; `git diff --check` passed; working tree was clean. This proves acceptance criteria 1-4.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Summary

- Established the locked Python 3.12 `uv` project and immutable normalized domain contract for namespaced ILIAS identities, courses, learning objects, upcoming items, artifacts, pagination, provenance, trust metadata, and stable failures.
- Added strict non-secret TOML/environment configuration with safe HTTPS/IDNA instance validation, bounded operational settings, portable IANA timezone validation, and resolved operator-controlled artifact locations.
- Added structured stderr-only operational logging with conservative secret/content redaction, fixed output fields, and process-scoped HMAC object pseudonyms.
- Kept later application, authentication, adapter, cache, artifact-store, extraction, CLI, and MCP work outside TASK-001.01.

## Verification

- `uv sync --locked`
- `uv run pytest -v` — 89 passed
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv lock --check`
- `git diff --check`
- Task-scoped reviews and final whole-branch review completed; no open Critical or Important findings.

## Risk / follow-up

A non-blocking test-quality minor remains around an assertion that compares keyed and unkeyed digest strings with different prefixes. The HMAC implementation, canonicalization, correlation, distinctness, and raw-ID nonleakage are independently covered.
<!-- SECTION:FINAL_SUMMARY:END -->
