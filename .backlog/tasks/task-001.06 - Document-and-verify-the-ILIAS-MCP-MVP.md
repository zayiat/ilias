---
id: TASK-001.06
title: Document and verify the ILIAS MCP MVP
status: To Do
assignee: []
created_date: '2026-08-20 17:04'
labels:
  - mcp
  - docs
  - verification
dependencies:
  - TASK-001.05
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1600
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the read-only server reproducibly installable and verifiable by a developer on Windows, including explicit login, Codex and Claude Code connection instructions, responsible-use limits, and safe opt-in live validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Documentation covers prerequisites, installation, configuration, interactive login, Codex and Claude Code MCP setup, Inspector usage, privacy, responsible access, errors, and troubleshooting.
- [ ] #2 Live smoke tests are disabled by default, require explicit local opt-in, and perform only bounded harmless reads.
- [ ] #3 A clean locked installation passes all non-live tests, formatting, linting, and type checks.
- [ ] #4 The MCP Inspector validates every schema and bounded fake response.
- [ ] #5 The documented fresh-session acceptance scenario lists active courses and 14-day upcoming items, opens a course, downloads a selected file, and extracts its text without manual ILIAS navigation.
- [ ] #6 Acceptance evidence contains pass or fail status only and no credentials, personal data, or course content.
<!-- AC:END -->
