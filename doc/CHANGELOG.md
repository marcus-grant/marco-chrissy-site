# Changelog

## 2025-12-11

## 2025-12-05

### Added

- Complete validate command functionality implementation
- DependencyValidator for Python dependency checking
- PermissionValidator for output directory permission verification  
- Proper exit code handling in validate command (returns 1 on failure)
- Comprehensive E2E test coverage for all validate functionality

### Changed  

- Removed skip decorators from validate E2E tests
- Enhanced validate command with dependencies and permissions checks
- Updated validator module with three specialized validator classes

### Documentation

- Added doc/commands/validate.md with complete validate command documentation
- Updated doc/modules/validator.md with:
  - DependencyValidator
  - PermissionValidator APIs
- Added validate command link to doc/commands/README.md
- Created doc/release/ archive structure for changelog organization
- Updated doc/README.md with release archive links

### Planning

- Comprehensive TDD plan for theme system implementation (Task 1.3)
- Test discovery methodology with placeholder implementations
- Complete MVP 0.1.0 release preparation tasks documented

### Tests

- Added theme system integration tests in test/e2e/test_theme_integration.py
- Integration test covers theme file loading, template rendering, CSS processing
- Tests for theme validation and PicoCSS integration prepared
- Added ThemeValidator unit tests with theme directory structure validation

### Added

- Theme directory validation system in galleria/theme/validator.py
- ThemeValidator class with validate_theme_directory method
- Validation for theme.json, templates/, and static/css/ structure
- Required template files: base.j2.html, gallery.j2.html, empty.j2.html
- Jinja2 template loading system in galleria/theme/loader.py
- TemplateLoader class with FileSystemLoader and template inheritance
- HTML autoescape support for security

### Refactored

- BasicTemplatePlugin now supports theme_path configuration
- Theme-based HTML generation with Jinja2 template rendering
- Fallback to hardcoded HTML when theme_path not configured
- Template data preparation with proper URL generation
- PicoCSS integration through theme base templates

## 2024-12-04

### Refactored

- Extract serve command business logic to orchestrator pattern for
  better testability and maintainability
- Split CLI concerns from serve orchestration logic in:
  - serve/orchestrator.py
  - serve/proxy.py
- Remove legacy test classes and enable all serve-related E2E tests
- Update serve architecture documentation with new separation of concerns pattern

### Fixed

- Resolve serve command hanging issue
  - Update unit tests to match new signal handler behavior
- Updated test_serve_orchestrator.py to reflect new architecture where
  signal handlers set stop events instead of calling cleanup directly
- Removed duplicate test methods causing ruff F811 errors
- All serve orchestrator unit tests now pass (11/11) with proper timeout handling

### Added

- E2E test for serve command URL override (skipped until implementation)
- BuildContext class for managing production vs development environment state
- PelicanBuilder URL override functionality for development vs production builds
- Mock config fixtures in test/conftest.py for consistent testing
- Template plugin URL filters for context-aware URL generation
- BasicTemplatePlugin BuildContext integration for development vs production URLs
- GalleriaBuilder BuildContext parameter support for pipeline coordination
- BuildOrchestrator BuildContext coordination for context-aware builds
- ServeOrchestrator class for coordinating build and proxy operations during serve

### Documentation

- Comprehensive BuildContext system documentation in architecture.md
- Updated build module documentation with BuildContext integration details
- Added template filters module documentation for context-aware URL generation
- Updated GalleriaBuilder API reference with new BuildContext parameters
- Added PLANNING.md with systematic task planning workflow and TDD methodology

## 2025-12-03

### Serve Command Architecture Refactor - Phase 2 Cycle 1

- **COMPLETED: ServeOrchestrator implementation with TDD methodology**
  - Created serve/ module structure with orchestrator.py  
  - Implemented ServeOrchestrator class for coordinating build and proxy operations
  - Added localhost URL override functionality for development server builds
  - Created comprehensive unit tests in test/unit/test_serve_orchestrator.py
  - Followed strict TDD workflow: Red → Green → Refactor cycle
  - Extracted orchestration logic from commented serve command implementation
  - All 2 orchestrator unit tests pass with proper BuildOrchestrator integration

- **COMPLETED: Proxy logic extraction to separate module**
  - Created serve/proxy.py with SiteServeProxy and ProxyHTTPHandler classes
  - Extracted all HTTP proxy logic from commented serve command implementation
  - Implemented request routing: /galleries/*→ Galleria, /pics/* → static, other → Pelican
  - Added subprocess management for Galleria and Pelican servers with cleanup
  - Created comprehensive unit tests in test/unit/test_serve_proxy.py (15 tests)
  - Updated ServeOrchestrator to use extracted proxy classes
  - Enhanced orchestrator tests with proper mocking to prevent server startup during testing

- **COMPLETED: CLI command simplified to handle only interface concerns**
  - Refactored cli/commands/serve.py to focus solely on argument parsing and orchestrator delegation
  - Removed all business logic from CLI command, delegating to ServeOrchestrator
  - Added proper error handling and user feedback for KeyboardInterrupt and exceptions
  - Updated CLI tests to work with new simplified interface (4 tests updated)
  - Removed skip decorators from CLI tests, now all pass with proper mocking
  - CLI command now follows single responsibility principle: parse args → call orchestrator → report results

- **KNOWN ISSUE: Serve command hangs indefinitely during execution**
  - E2E tests timeout after 2 minutes when testing actual serve command
  - Server startup appears to work but servers don't terminate cleanly
  - Unit tests pass with mocking, but real execution has blocking issue
  - Need to debug server lifecycle and cleanup in ServeOrchestrator
  - Architecture refactor complete but needs server management fixes

## 2025-12-02

### Fix: Pelican Index Page Conflict Resolution

- **RESOLVED: Build system automatically handles index page conflicts**
  - Fixed "File to be overwritten" errors when content contains pages with `slug: index`
  - Added smart detection of conflicting content during build process
  - Conditionally disables Pelican's default blog index when custom index pages exist
  - Zero configuration required - system automatically adapts to content structure
  - Both scenarios now work seamlessly: custom index pages and default blog index
  - Manual workaround (`rm output/index.html && site build`) no longer needed
  - Added comprehensive test coverage for both conflict scenarios
  - Updated documentation across configuration, architecture, and build command guides

### Fix: Proxy Routing Bug in Serve Command  

- **Fixed proxy routing for /galleries/* URLs** - now routes correctly to Galleria server

### Fix: Galleria Manifest Path Bug in Serve E2E Tests

- **Fixed serve E2E tests** - use absolute paths and create pre-existing manifest files

### Serve Command Issues Identified

- **REMAINING: Critical blocking issues for real-world serve command usage**
  - Found Galleria CPU hang issue with large photo collections (645 photos at 99.9% CPU)
  - Identified missing --no-generate flag needed for development workflow
  - Additional issues: Pelican routing problems, photo links not going to full-sized photos

### Site Serve Command Complete

- **COMPLETED: Site serve E2E test enablement and fixes**
  - Enabled all skipped E2E tests for serve command functionality
  - Fixed config file format mismatch (.toml → .json) in serve implementation
  - Enhanced galleria test fixtures with required output_dir and manifest_path
  - Both E2E serve tests now pass consistently in ~4 seconds
  - Complete TDD workflow: enable test → identify issues → fix → verify
  - All 380 tests pass with comprehensive serve command coverage

- **COMPLETED: HTTP server startup implementation in serve command**
  - Added actual HTTP server creation and startup to serve() function
  - Implemented automatic backend server startup for Galleria and Pelican
  - Added graceful shutdown handling with Ctrl+C support
  - Fixed Galleria command to use --config flag instead of positional argument
  - Enhanced E2E test with basic output directory setup for Pelican
  - Added comprehensive unit test for server integration workflow
  - Serve command now fully functional for development workflow
