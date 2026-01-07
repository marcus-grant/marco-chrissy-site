# Handoff Documentation Template

## Purpose
Standard template for handing off work between development sessions. Ensures continuity, proper context transfer, and clear next steps for resuming work.

## When to Use
- Switching between major phases or cycles
- When encountering blocking issues that require fresh perspective
- Before long breaks in development work

## Handoff Template Structure

1. **Essential Context Documents** - Links to doc/README.md, doc/TODO.md, and doc/CONTRIBUTE.md
2. **Key Development Rules** - Abridged critical guidelines from CONTRIBUTE.md
3. **PR Context & Goal** - Current branch and high-level objective
4. **Recently Completed** - Summary of work just finished
5. **What's Next** - Current TODO.md tasks and specific files to work on
6. **Handoff Instructions** - This template reference for next handoff
7. **Copy-paste Message** - Brief summary for immediate context

## Section Details

### 1. Essential Context Documents
- `doc/README.md` - Project overview and documentation structure
- `doc/TODO.md` - Current task roadmap and active work items
- `doc/CONTRIBUTE.md` - Development workflow rules and testing requirements

### 2. Key Development Rules (Abridged)
- TDD Required: Every feature starts with failing tests
- Small Commits: Maximum 200-300 lines per commit
- Testing Sequence: `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- Environment Variables: NEVER read/inspect env var values
- Test Isolation: All tests use isolated temp filesystems
- Commit Prefixes: Tst:, Ft:, Fix:, Ref:, Doc:, Pln:

### 3. PR Context & Goal
- Current branch name
- High-level feature/goal being implemented
- Overall objective and success criteria

### 4. Recently Completed
- Specific tasks that were just finished
- Key discoveries or learnings from the work
- Any architectural decisions made

### 5. What's Next
- Current section/phase from TODO.md
- Specific tasks to tackle next
- Key files that need work
- Any blocking issues or dependencies

### 6. Handoff Instructions
- Reference to this template (doc/HANDOFF.md)
- Reminder about the copy-paste message format

### 7. Copy-paste Message
- Brief 2-3 sentence summary for immediate context
- Current branch and main objective
- Next immediate task

## Example Template

```
Handoff Message

Essential Context Documents
Primary References:
1. doc/README.md - Project overview and documentation structure
2. doc/TODO.md - Current task roadmap and detailed Phase X plan
3. doc/CONTRIBUTE.md - Development workflow rules and testing requirements

Key Development Rules (Abridged from CONTRIBUTE.md)
- TDD Required: Every feature starts with failing tests
- Small Commits: Maximum 200-300 lines per commit
- Testing Sequence: uv run ruff check --fix --unsafe-fixes && uv run pytest
- Environment Variables: NEVER read/inspect env var values
- Test Isolation: All tests use isolated temp filesystems

PR Context & Goal
Branch: ft/feature-name
Goal: [High-level objective and success criteria]

Recently Completed
- [Specific completed tasks]
- [Key discoveries]

What's Next (from TODO.md)
Currently In: Phase X, Cycle Y
Next Tasks: [Specific items from TODO.md]

Copy-paste message for next context:
[Brief 2-3 sentence summary with branch, objective, and next task]
```