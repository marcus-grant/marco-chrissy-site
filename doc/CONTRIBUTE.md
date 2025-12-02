# Development Guidelines

## Important Donts

* NEVER EVER READ SHELL ENV VARIABLES
* Don't commit code without ruff linting checks and full test suite runs
* Never implement without associated test

## Planning Process for doc/TODO.md

When adding complex features, update doc/TODO.md with concrete, actionable tasks that spell out the entire workflow:

### Task Structure

Each task must specify exactly:
* **What to implement/test** (specific files, classes, methods)
* **Pre-commit workflow**: `uv run ruff check --fix --unsafe-fixes`, `uv run pytest`, update docs
* **Commit message format**: `Prefix: Description`
* **Expected outcome** (tests pass/fail, what functionality works)

### Task Organization
* **E2E/Integration tests first** - Mark with `@pytest.mark.skip`, own commit
* **Unit test cycles** - RED → GREEN → refactor → commit (200-300 LOC max)
* **Implementation follows TDD** - Write failing tests, implement to pass
* **Documentation tasks last** - Batch doc updates after functionality complete

### Example Task Format

```
- [ ] **Create galleria serve E2E tests (skipped)**
  - [ ] Create `galleria/test/test_serve_e2e.py` with tests:
    - [ ] `@pytest.mark.skip` test_serve_cli_integration - Test CLI starts server
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest` (tests should be skipped)
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Tst: Add galleria serve E2E tests (skipped)`
```

### Key Principles
* **No workflow explanation in tasks** - Tasks ARE the workflow, step by step
* **Concrete file paths** - Specify exact files to create/modify
* **Self-contained** - Each task can be completed independently across context breaks
* **Pre-commit checks mandatory** - Every commit includes ruff + pytest + doc updates

## Testing Requirements

* This is a `**uv**`` managed project
  * **Test Command**: Use `uv run pytest` to run tests
    * **NOT**: `python -m pytest`
* **ALWAYS run ruff first**: `uv run ruff check --fix --unsafe-fixes` before testing
* **ALWAYS run full test suite**: Before every single commit
* **Specific Test Files**:
  * Use `uv run pytest test/test_filename.py -v` for focused testing
  * **See Code Quality Workflow below** for complete pre-commit sequence
* Follow Nested TDD Workflow (see [workflow.md](workflow.md) for full details):
  * Also see [testing.md](./testing.md) for testing details and fixtures

  **Outer Cycle (E2E/Integration Tests)**:
  * Write E2E test for desired functionality - mark with `@pytest.skip` initially
  * Run test - should be skipped, keeping test suite green
  * This defines what needs to be built and drives inner cycle
  * Only unskip when ready to verify complete functionality

  **Inner Cycle (Unit TDD)**:
  * Write unit test for specific missing functionality identified by E2E test
  * Run test - ensure it fails as expected (Red)
  * Implement minimal code to make test pass (Green)
  * Refactor for better solution while keeping test green (Refactor)
  * Commit small change (typically <300 LOC)
  * Repeat for next piece of missing functionality

  **Documentation Cycle**:
  * After several commits in TDD cycles, update documentation in batch
  * Use shared fixtures (`temp_filesystem`, `config_file_factory`) for consistent test setup
  * Make separate `Doc:` prefixed commit for documentation changes

  **Key Success Patterns**:
  * **Always passing suite** - Skip pattern keeps tests green during development
  * **Real filesystem tests** - Use fixtures with actual files, not mocks
  * **Small, focused commits** - Each unit test cycle produces complete, testable change
  * **Clear handoff points** - E2E tests show exactly what needs implementing
  * If a problem is discovered outside automated testing...
    * That means the tests are bad, not the implementation
    * That means tests need updating first, not the implementation
* Task management:
  * Every test should usually only cover one TODO task
  * Some tasks require multiple tests
  * After test(s) pass and refactors complete next step is next note...
* Pre-commit documentation process:
  * Mark completed TODO items as done
  * Add entry to doc/CHANGELOG.md with H2 date header and bullet points
  * Document architectural decisions in doc/architecture/ or doc/modules/
  * Delete completed TODO entries to prevent size explosion
  * TODO should shrink overall as MVP approaches completion
* Documentation updates (Green phase):
  * When tests pass, update relevant documentation in `doc/`
  * Each subdirectory in `doc/` represents a topic
  * **Documentation linking rule**: Only link to build adjacency lists
    * Each README links to peer documents + immediate subdirectory READMEs only
    * No deep linking from higher-level READMEs
    * Creates clean hierarchical navigation: doc/README → topic directories → topic documents
  * **CRITICAL**: Every document must be linked in the documentation hierarchy starting from doc/README.md
  * No document should be a link orphan - all must be discoverable through the hierarchy
* Implement in small steps with clear logical breaks:
  * Add one test case or feature at a time
  * Test immediately after each testable addition
  * Never write massive amounts of code without testing

## Code Quality Workflow

**CRITICAL: Always follow this exact sequence before every commit:**

1. **Write/modify code** - Implement your changes
2. **Run ruff with fixes** - `uv run ruff check --fix --unsafe-fixes`
3. **Run relevant tests** - Verify formatting didn't break logic
4. **Run full test suite** - `uv run pytest` (before every commit)
5. **Commit** - Only if all tests pass

**Why this order matters:**
* Ruff auto-fixes can change code logic (rare but possible)
* Style changes can break tests in unexpected ways  
* Catching issues early prevents context pollution from easy-to-fix errors

**Never skip step 3** - always test after ruff formatting.

## Commit Message Format

* Title: Maximum 50 characters including prefix
* Body: Maximum 72 characters per line
* Body text should use '-' bullets with proper nesting
* Use prefixes:
  * `Tst:` for test-related changes
  * `Fix:` for bug fixes
  * `Ft:` for new features
  * `Ref:` for refactoring
  * `Doc:` for documentation
  * `Pln:` for planning/TODO updates
* No signature block - do not include emoji, links, or Co-Authored-By lines

## Commit Size Limits

* **NEVER create commits with 1000+ line changes**
* Maximum recommended commit size: 200-300 lines of changes
* If a logical unit of work exceeds this:
  * Break into smaller, logically cohesive commits
  * Use multiple commits that build on each other
  * Each commit should still be complete and testable
* Prefer many small commits over few large commits
* Exception: Initial file creation or large refactoring may exceed limits if unavoidable

## Code Style

* Follow existing patterns in the codebase
* Check neighboring files for conventions
* Never assume a library is available - verify in package.json/requirements
* Functions should have a proper docstring
* We type annotate our code and prefer dataclasses for basic data structures
* Match indentation and formatting of existing code
* Follow PEP 8, ruff and typical Python conventions:
  * No trailing whitespace
  * Blank line at end of file
  * Two blank lines between top-level definitions
  * One blank line between method definitions
  * Spaces around operators and after commas
  * No unnecessary blank lines within functions
  * Maximum line length of 88 characters (Black/Ruff default)
* **2-space indentation** throughout templates and JS
  * **NOT** Python - Python uses 4 spaces

## Galleria Development Rules

* All HTML, CSS, and JS generation must be designed with plugin extensibility in mind from day one.

## Module Organization Rules

* Avoid catch-all patterns like 'core' or 'util' directories
* 'util' only acceptable for singular-purpose modules with simple, testable, pure functions
* Split generic vs domain-specific modules clearly
* Domain logic gets specific directories (e.g., galleria/template for all templating)

## Command System Rules

* Each command calls only its immediate predecessor (cascading pattern)
* Commands chain automatically: `deploy` → `build` → `organize` → `validate`
* No command should call multiple other commands directly
* Fail fast with validation before expensive operations

## Security & Deployment Rules

* WE CAN NOT ALLOW CREDENTIALS TO LEAK
* Sensitive configurations read from env vars
* Code may look at env var values but NEVER read env vars directly
* Only venv-related env vars are acceptable to read
* Must guide user on what deployment commands to call

## Project-Specific Instructions

* This is a customized site builder
* The galleria directory will eventually split out to a separate imported package
  * So ensure there's very loose coupling from rest of project
  * Consider how this part will eventually split out
  * Should be generalizable and easy to integrate in other projects.

## Testing Infrastructure

* **Use shared fixtures** (see [testing.md](testing.md)):
  * `temp_filesystem` - Isolated temporary directories
  * `file_factory` - Create files with content (text or JSON)
  * `config_file_factory` - Config files with sensible defaults
  * `full_config_setup` - Complete config environment
* **Real filesystem tests** - Prefer actual files over mocks for integration tests
* **Temporary filesystem isolation** - E2E tests use subprocess calls in temp directories

## Documentation Management

* Keep TODO.md updated:
  * Update "Current Tasks" section when starting/stopping work
  * Mark completed items with [x]
  * Add new tasks as they're discovered
  * Document progress for easy resumption
  * When I say delete from TODO, only when its section of the TODO is complete.
* Keep `./doc` updated
  * `doc/README.md`
    * The overview and index to other documentation documents
  * The rest are named after key documentation topics
  * If a new documentation topic is needed:
    * Check if a pre-existing document just needs updating or adding to
      * If not - check with topic directory it should be in
        * If a new one is needed - create a new topic directory/subdir
  * Ensure a chain of doc links leading from project root README to doc exists
* The only document every contribution should need is the root README.md
  * From there it should be clear what if any other documents need reading
* Update CHANGELOG.md when warranted by significant functionality changes
* Documentation should be **concise and practical** - focus on what developers need

## Important Reminders

* Do what has been asked; nothing more, nothing less
* NEVER create files unless they're absolutely necessary for achieving your goal
* ALWAYS prefer editing an existing file to creating a new one
