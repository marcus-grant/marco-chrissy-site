# Development Guidelines

## Important Donts

* NEVER EVER READ SHELL ENV VARIABLES
* Don't commit code without ruff linting checks and full test suite runs
* Never implement without associated test

## Testing Requirements

* This is a `**uv**`` managed project
  * **Test Command**: Use `uv run pytest` to run tests
    * **NOT**: `python -m pytest`
* **Specific Test Files**:
  * Use `uv run pytest test/test_filename.py -v` for focused testing
  * **ALWAYS** run full suites before every commit
* Follow E2E + TDD approach:
  * E2E/Integration tests to surface larger missing or broken pieces
    * Therefore they should be prioritized first
    * Nest into Unit tests when missing or broken piece discovered
      * Should try and find existing tests needing modification first.
      * If no test exists for that spec, make a new one
  * TDD fills or fixes those pieces incrementally
  * Build tests singularly first
  * Ensure test fails as expected (red)
  * Implement change to make test pass (green)
  * Consider refactors for better solution (refactor)
  * Move to next test when complete or to parent integration/E2E test
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
  * Follow documentation hierarchy: documents link to same-level README → subdirectory README → parent README
  * Only top-level README provides high-level overviews and links to directory-level or subdirectory READMEs
  * **CRITICAL**: Every document must be linked in the documentation hierarchy starting from doc/README.md
  * No document should be a link orphan - all must be discoverable through the hierarchy
* Implement in small steps with clear logical breaks:
  * Add one test case or feature at a time
  * Test immediately after each testable addition
  * Never write massive amounts of code without testing

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

## Project-Specific Instructions

* This is a customized site builder
* The galleria directory will eventually split out to a separate imported package
  * So ensure there's very loose coupling from rest of project
  * Consider how this part will eventually split out
  * Should be generalizable and easy to integrate in other projects.
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

## Important Reminders

* Do what has been asked; nothing more, nothing less
* NEVER create files unless they're absolutely necessary for achieving your goal
* ALWAYS prefer editing an existing file to creating a new one
