# Project Agent Guidance

## Upstream issue and PR work

When a task selects, designs, implements, reviews, resumes or updates an upstream GitHub issue/PR, read `skills/upstream-issue-pr/SKILL.md` before acting. Use `skills/upstream-issue-pr/references/verification.md` for acceptance coverage, review evidence and delivery status.

The guidance is host-neutral and applies equally to Codex, Cursor, OpenCode, Claude Code and other coding agents. Keep its canonical rules in that skill; do not create host-specific copies that can drift.

## Independent development audit

For an independent audit of the development workflow or an upstream issue/PR change, use `agents/upstream-issue-auditor.md` as a fresh-context subagent role. Give it only the task, repository path, audit scope and rule paths. Keep it read-only and max depth 1; the parent agent owns reproduction and any fixes.

Cursor registers the same role through `.cursor/agents/upstream-issue-auditor.md`; invoke it with `/upstream-issue-auditor` or ask for that subagent by name. The Cursor file is only a thin loader and does not fork the canonical rules.
