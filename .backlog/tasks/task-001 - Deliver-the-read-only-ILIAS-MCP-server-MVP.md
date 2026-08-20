---
id: TASK-001
title: Deliver the read-only ILIAS MCP server MVP
status: To Do
assignee: []
created_date: '2026-08-20 17:02'
labels:
  - mcp
  - ilias
  - mvp
dependencies: []
references:
  - >-
    https://ilias3.uni-stuttgart.de/login.php?client_id=Uni_Stuttgart&cmd=force_login&lang=en
  - 'https://github.com/modelcontextprotocol/python-sdk'
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
priority: high
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a private, local MCP server for a student to inspect their own University of Stuttgart ILIAS account from Codex, Claude Code, and compatible clients. The MVP is read-only and covers active courses, normalized learning objects, structured deadlines and calendar events, controlled file downloads, and local document text extraction. It must use English interfaces over stdio, keep credentials outside MCP and repository content, mark authored content as untrusted, bound all result sets, and fail closed when the Stuttgart web interface is incompatible. Later OCR, transcription, submissions, additional instances, and public distribution are outside this feature.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A fresh MCP client session can list active courses and structured upcoming items for the next 14 days without manual ILIAS navigation.
- [ ] #2 A client can inspect a selected course and learning object through stable English schemas with provenance and untrusted-content metadata.
- [ ] #3 A client can download an authorized file into server-controlled storage and locally extract supported HTML, PDF, or Office text.
- [ ] #4 Expired authentication, unavailable ILIAS, rate limits, unsupported content, oversized content, invalid cursors, and adapter incompatibility return stable actionable errors.
- [ ] #5 Credentials, session material, personal data, and course content are absent from repository content and operational logs.
- [ ] #6 All non-live automated tests, static checks, and documented MCP acceptance checks pass on Windows with Python 3.12.
<!-- AC:END -->
