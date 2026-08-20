---
id: TASK-001.03
title: Read University of Stuttgart ILIAS safely
status: To Do
assignee: []
created_date: '2026-08-20 17:03'
labels:
  - ilias
  - adapter
dependencies:
  - TASK-001.02
references:
  - >-
    https://ilias3.uni-stuttgart.de/login.php?client_id=Uni_Stuttgart&cmd=force_login&lang=en
documentation:
  - docs/superpowers/specs/2026-08-20-ilias-mcp-server-design.md
  - docs/superpowers/plans/2026-08-20-ilias-mcp-server-mvp.md
parent_task_id: TASK-001
priority: high
type: task
ordinal: 1300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide the University of Stuttgart instance integration needed to normalize the authenticated student's visible courses, learning objects, deadlines, calendar events, and file references. The integration must use conservative request behavior and disable affected capabilities rather than guess when the ILIAS interface changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Sanitized fixture tests cover course lists, object hierarchies, details, deadlines, calendar events, empty states, expired sessions, maintenance, and unknown visible types.
- [ ] #2 Fixture checks reject secrets, personal identifiers, and real course material.
- [ ] #3 Requests reuse the local session, remain rate-limited and bounded, honor server retry guidance, and access only visible discovered URLs.
- [ ] #4 Missing required page structure produces adapter-incompatible errors rather than partial plausible data.
- [ ] #5 The adapter satisfies the same read-only interface as the deterministic fake.
<!-- AC:END -->
