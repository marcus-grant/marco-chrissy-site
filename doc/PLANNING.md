# Planning Workflow Guide

## Overview

This document defines the systematic approach to
planning development tasks that naturally enforces the workflow rules defined in
[`CONTRIBUTE.md`](CONTRIBUTE.md).
By following these planning patterns,
any developer can maintain consistent, high-quality development practices.

>**The key principle:** Tasks in [`TODO.md`](TODO.md) should be structured so
that following them automatically results in following our development workflow.

## Core Planning Principles

### 1. Test-Driven Development (TDD)

- Every feature starts with failing tests
- Implementation follows to make tests pass
- Refactoring improves code while maintaining green tests
- If bugs are discovered outside this flow,
  that means the tests are insufficient and need to be improved
  - Only then can you fix implementation bugs to satisfy the new tests

### 2. Small, Focused Commits

- Maximum 200-300 lines of changes per commit
- Each commit should be complete and testable
- Each commit should have a clear purpose
- Clear commit message prefixes (`Ft:`, `Fix:`, `Tst:`, `Doc:`, `Ref:`, `Pln:`)

### 3. Nested Test Strategy

- **E2E/Integration tests** define the overall functionality (initially skipped)
- **Unit tests** implement specific pieces identified by E2E failures
- **Skip pattern** keeps test suite green during development

### 4. Documentation-Driven Development

- Document architectural decisions as they're made
- Maintain adjacency-linked documentation structure
- Update CHANGELOG.md for user-visible changes
- Update TODO.md to reflect current task status
- As a final commit to a PR:
  - Check documentation that exists by following links from doc/README.md
  - Consider if any document's content needs updating
  - Consider if any new documents are needed

## Task Planning Template

### Subsection Naming

Use descriptive names that convey the actual work being done. Avoid:
- Generic terms like "Phase", "Task", "Cycle", "Commit", "Step"
- Numbering (1, 2, 3 or 1.1, 1.2)

**Good**: `**Config Validation**`, `*Extract Proxy Logic*`, `**CLI Integration**`
**Bad**: `**Phase 1: Setup**`, `*Cycle 2*`, `**Task 1.1**`

The structure itself provides ordering - names should describe content.

### Top-Level Task Structure

Every major feature or refactor should follow this pattern:

```markdown
### Task: [Feature Name] (Branch: `prefix/branch-name`)

*Problem Statement: Brief description of what needs solving and why*

**Setup & E2E Definition**
- [ ] `git checkout -b prefix/branch-name`
- [ ] Create E2E test in `test/e2e/test_feature_name.py`
  - [ ] Test should verify end-to-end functionality
  - [ ] Add `@pytest.mark.skip("Feature not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for feature (skipped)`

**TDD Implementation**
[Repeat for each logical unit of work]

- [ ] Create/modify stub in `path/to/module.py`
- [ ] Write unit test for `SpecificFunctionality` that fails
- [ ] Implement minimal code to pass test
- [ ] Refactor for better design (keeping tests green)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Implement specific functionality`

**Integration & Documentation**
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes (if not, continue TDD)
- [ ] Update relevant documentation in `doc/`
- [ ] Ensure documentation links are maintained
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Update documentation for feature`

**Version & Release**
- [ ] Discuss version bump with project manager (patch/minor/major)
- [ ] Update version in `pyproject.toml` and `galleria/__main__.py`
- [ ] For minor/major bumps: migrate CHANGELOG.md entries to `doc/release/X-Y.md`
  - [ ] Move all timestamped sections to release archive
  - [ ] Leave only header and format sections in CHANGELOG.md
- [ ] Commit: `Ft: Bump version to X.Y.Z`

**PR Creation**
- [ ] `gh pr create --title "Prefix: Feature description" --body "Implementation details"`
```

## Concrete Planning Example

### Task Example: Extract Serve Command Logic

```markdown
### Task: Serve Command Architecture Refactor (Branch: `ref/serve`)

*Problem Statement: Serve command violates separation of concerns by mixing CLI handling with HTTP proxy logic, build orchestration, and server management. This causes test isolation issues and makes the command difficult to test properly.*

**Setup & E2E Definition**
- [ ] `git checkout -b ref/serve`
- [ ] Create E2E test in `test/e2e/test_serve_refactor.py`
  - [ ] Test that serve command properly delegates to orchestrator
  - [ ] Verify CLI args are parsed and passed correctly
  - [ ] Add `@pytest.mark.skip("Refactor not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for serve refactor (skipped)`

**TDD Implementation**

*Create Serve Orchestrator*
- [ ] Create stub `serve/orchestrator.py` with `ServeOrchestrator` class
- [ ] Write unit test for `ServeOrchestrator.start()` that fails
- [ ] Implement basic orchestrator structure
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add ServeOrchestrator class structure`

*Extract Proxy Logic*
- [ ] Write unit test for proxy delegation that fails
- [ ] Move `SiteServeProxy` to `serve/proxy.py`
- [ ] Update orchestrator to use extracted proxy
- [ ] Fix broken imports in existing tests
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Extract proxy logic to separate module`

*Simplify CLI Command*
- [ ] Write unit test for simplified CLI interface that fails
- [ ] Refactor `cli/commands/serve.py` to only handle:
  - [ ] Argument parsing
  - [ ] Calling orchestrator
  - [ ] Result reporting
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Simplify serve command to CLI-only concerns`

**Integration & Documentation**
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes
- [ ] Update `doc/modules/serve/README.md` with new architecture
- [ ] Update `doc/commands/serve.md` with simplified interface
- [ ] Update `doc/architecture.md` with separation of concerns explanation
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Update serve architecture documentation`

**Version & Release**
- [ ] Discuss version bump with project manager (patch/minor/major)
- [ ] Update version in `pyproject.toml` and `galleria/__main__.py`
- [ ] For minor/major bumps: migrate CHANGELOG.md entries to `doc/release/X-Y.md`
  - [ ] Move all timestamped sections to release archive
  - [ ] Leave only header and format sections in CHANGELOG.md
- [ ] Commit: `Ft: Bump version to X.Y.Z`

**PR Creation**
- [ ] `gh pr create --title "Ref: Extract serve command business logic" --body "..."`
```

## Planning Guidelines

### When to Create a New Task

1. **Feature Addition**: New user-visible functionality
2. **Architecture Refactor**: Significant code organization changes
3. **Bug Fixes**: Issues that require multiple commits to resolve properly
4. **Documentation Updates**: Major documentation restructuring

### Task Sizing Guidelines

- **Small Task**: 1-3 TDD cycles, 1-5 commits, <500 lines changed
- **Medium Task**: 4-8 TDD cycles, 5-10 commits, 500-1500 lines changed  
- **Large Task**: Should be broken into multiple smaller tasks

### Quality Gates

Each phase must be completed before moving to the next:

1. **All tests pass** (including skipped ones)
2. **Ruff formatting** applied without errors
3. **Documentation updated** and linked properly
4. **CHANGELOG.md updated** for user-visible changes
5. **TODO.md updated** to reflect current status

### Commit Message Patterns

- `Tst:` - Test creation or modification
- `Ft:` - New feature implementation  
- `Fix:` - Bug fixes
- `Ref:` - Refactoring (no functional changes)
- `Doc:` - Documentation updates
- `Pln:` - Planning and TODO updates

### Branch Naming Conventions

- `ft/feature-name` - New features
- `fix/issue-description` - Bug fixes
- `ref/refactor-target` - Refactoring work
- `doc/topic` - Documentation updates

## Integration with CONTRIBUTE.md

This planning approach automatically enforces the rules in CONTRIBUTE.md:

- **No massive commits**: TDD cycles keep commits small
- **Testing requirements**: E2E + unit test pattern ensures coverage
- **Documentation**: Phase 3 requires doc updates
- **Code quality**: Ruff + pytest run before every commit
- **Clear handoffs**: Each phase completion provides natural stopping points

## Troubleshooting Common Planning Issues

### "Task is too complex"

**Solution**: Break into smaller tasks with clear dependencies

### "Tests are failing unexpectedly"  

**Solution**: Return to previous working state, add more unit tests

### "Code quality checks failing"

**Solution**: Run `uv run ruff check --fix --unsafe-fixes` and address remaining issues

### "Documentation links broken"

**Solution**: Verify adjacency-list structure in doc/ hierarchy

### "Commit messages inconsistent"

**Solution**: Use the prefix patterns defined above consistently

## Benefits of This Approach

1. **Predictable workflow**: Same pattern for every task
2. **Quality assurance**: Multiple gates ensure high standards
3. **Easy handoffs**: Clear phase completions enable context switching
4. **Maintainable TODO**: Tasks naturally stay organized and actionable
5. **Natural TDD**: Structure makes it harder to skip testing
6. **Documentation debt prevention**: Doc updates are built into workflow

