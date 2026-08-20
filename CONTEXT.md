# ILIAS MCP Context

This context defines the learning-platform concepts exposed through the local MCP server. It keeps ILIAS-specific language stable across adapters and MCP clients.

## Language

**ILIAS Instance**:
An independently operated ILIAS installation with its own URL, authentication, configuration, and object identifiers.
_Avoid_: Server, tenant, site

**Learning Object**:
A typed item visible inside an ILIAS course, such as a file, exercise, forum, test, survey, group, or learning module.
_Avoid_: Module, item, content

**Course**:
An enrolled ILIAS course that contains learning objects and may be active or inactive.
_Avoid_: Module, class

**Upcoming Item**:
A structured ILIAS deadline or calendar event associated with the authenticated user and optionally a course.
_Avoid_: To-do, task, inferred deadline

**Submission Draft**:
One or more files uploaded to an exercise without completing any separately available final-submission action.
_Avoid_: Submission, final submission

**Final Submission**:
An explicit, potentially irreversible action that marks a submission as complete when the ILIAS instance supports that distinction.
_Avoid_: Upload, submission draft

**Artifact**:
A server-managed local copy of an ILIAS file, identified by metadata and a checksum and eligible for extraction.
_Avoid_: Arbitrary local file, attachment

**Dashboard Context**:
A deterministic, compact collection of active courses, upcoming items, and relevant learning-object metadata intended for an MCP client to summarize.
_Avoid_: AI summary, dashboard scrape

