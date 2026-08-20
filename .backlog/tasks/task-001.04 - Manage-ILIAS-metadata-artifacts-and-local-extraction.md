---
id: TASK-001.04
title: Manage ILIAS metadata artifacts and local extraction
status: To Do
assignee: []
created_date: '2026-08-20 17:03'
labels:
  - ilias
  - documents
  - security
dependencies:
  - TASK-001.03
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1400
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add bounded metadata freshness, controlled local file artifacts, and local text extraction for authorized HTML, PDF, and Office documents. The capability must not permit arbitrary filesystem access or send course material to external services.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Metadata caching supports short expiry and explicit scoped refresh without storing credentials or document content.
- [ ] #2 Downloads use server-controlled storage with atomic writes, checksums, expiry, size limits, and path-traversal and symlink-escape protection.
- [ ] #3 Extraction accepts only server-created artifacts and supports bounded HTML, PDF, DOCX, XLSX, and PPTX text extraction.
- [ ] #4 Extraction reports provenance and truncation and handles corrupt, unsupported, oversized, or decompression-heavy content safely.
- [ ] #5 Automated tests prove that extraction performs no outbound network calls.
<!-- AC:END -->
