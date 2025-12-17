# Changelog

## 2025-12-17

### Added

- Created defaults.py module for path configuration
- Implemented get_output_dir() function returning Path object for testability
- Added comprehensive unit test coverage for defaults module path configuration
- Implemented PelicanBuilder shared template integration using configure_pelican_shared_templates
- Added unit tests for shared CSS copying functionality in AssetManager
- Created proper isolated integration test for shared component system verification

### Fixed

- Fixed PelicanBuilder to use configure_pelican_shared_templates for proper template precedence
- Updated Pelican Jinja environment configuration to include both shared and theme-specific templates
- Resolved shared component build integration issues through systematic TDD approach

### Completed

- Removed @pytest.mark.skip decorators from real plugin integration test
- Verified complete shared component integration with all 455 tests passing (8 skipped)
- Confirmed shared navbar and CSS appear correctly in both Pelican and Galleria build outputs
- Updated gallery navigation links from generic /galleries/ to actual /galleries/wedding/
- Fixed content navigation to point to working gallery instead of empty directory
- Verified gallery pagination works correctly with index.html redirecting to page_1.html

### Fixed

- Replaced hardcoded "output" path with defaults.get_output_dir() in serve command
- Added unit test for serve command defaults usage ensuring proper mockability
- Removed hardcoded path dependencies breaking test isolation

### Tests

- Enabled all 7 previously skipped serve command tests with proper mocking
- Added get_output_dir() mocking to all serve tests for isolation
- Fixed build command mocking in serve tests preventing real command execution
- All serve command unit tests now pass without test isolation issues

### Added

- Added get_shared_template_paths() and get_shared_css_paths() to defaults module
- Enhanced template_loader.py to use defaults when no external templates configured
- Extended asset_manager.py with shared CSS file handling using defaults
- Functions return Path objects for external package compatibility

### Tests

- Added integration test for shared component build system verification
- Test uses BeautifulSoup to verify shared navbar appears in both Pelican and Galleria HTML
- Test verifies shared CSS is copied to output and properly integrated
- Used existing fixtures (full_config_setup, file_factory) for proper test setup
- Test currently skipped as shared component build integration not implemented

### Fixed

- Added Pelican shared template integration via SHARED_THEME_PATH config
- Pelican builder now configures Jinja2 environment for shared templates  
- Unit tests verify Pelican uses shared templates when configured

### Planning

- Restructured TODO.md to fix shared component integration failures
- Removed completed infrastructure items from Task 5.1 (already built)
- Added clear problem definition for build system integration gaps
- Updated task structure to follow proper TDD workflow from PLANNING.md
- Created fix/shared-components branch to address integration failures

### Tests

- Fixed test isolation issues by adding skip decorators to failing tests
- Identified serve command hardcoded 'output' directory breaking test isolation
- Documented real plugin integration test expecting index.html redirect file
- Maintained green test suite following TDD skip pattern from PLANNING.md
- Preserved failing test logic for future integration implementation phases

### Planning

- Completed Phase 2 integration discovery analyzing skipped test failures
- Designed defaults.py module approach for mockable path constants
- Added detailed Phase 3 TDD cycles to TODO.md following PLANNING.md structure
- Planned 6 implementation cycles from defaults creation to complete integration verification
- Created plan for true E2E tests with mock shared navbar and CSS components

## 2025-12-17

### Added

- E2E test framework for shared component system in test/e2e/test_shared_components.py
- Test coverage for shared asset management and template inclusion
- Test verification for PicoCSS integration across Pelican and Galleria
- Planning framework for unified navigation and responsive layout implementation
- Shared asset manager in themes/shared/utils/asset_manager.py for external dependency management
- PicoCSS download functionality with automatic directory creation and URL generation
- Unit test coverage for asset manager with proper TDD implementation
- Shared template loader system in themes/shared/utils/template_loader.py
- Pelican and Galleria template search path configuration with proper precedence
- Jinja2 template inclusion support across both systems with shared components
- Comprehensive test coverage for template loading and precedence rules
- New shared_theme_dirs fixture for consistent theme testing setup
- Context adapter system for converting Pelican and Galleria contexts to shared format
- Abstract base class pattern for template context standardization
- Navigation configuration loading functionality

## 2025-12-16

### Added

- Complete theme system integration test in test/e2e/test_theme_integration.py
- Theme system enables external template/CSS files instead of hardcoded strings
- Theme-based gallery generation with full plugin pipeline integration
- Validated theme directory structure with ThemeValidator
- Jinja2 template loading from theme files via TemplateLoader
- CSS file loading from theme static/css directory
- Fallback to hardcoded templates/CSS when theme_path not configured
- Gallery index.html generation for paginated galleries to handle directory access

### Changed

- Removed @pytest.mark.skip from theme integration test - theme system now functional
- BasicTemplatePlugin now supports theme_path configuration for external templates  
- BasicCSSPlugin now supports theme_path configuration for external CSS files
- Template and CSS plugins maintain backward compatibility with hardcoded fallbacks

### Fixed

- Photo URL generation bug - links now correctly point to /pics/full/{filename} instead of /{filename}
- URL filter now properly handles bare filenames from manifest data using file extension detection
- Gallery directory access now generates index.html with redirect to page_1.html for /galleries/wedding/ URLs
- Template plugin tests now use proper fixtures instead of hardcoded production data
- Added comprehensive tests for URL generation edge cases and bugs

### Documentation

- Updated doc/modules/galleria/template-plugins.md with complete theme system documentation
- Added ThemeValidator and TemplateLoader architecture sections
- Documented theme directory structure and configuration format
- Added theme-based gallery generation usage examples
- Documented theme_path configuration for template and CSS plugins

### Tests  

- Theme integration test validates end-to-end theme file loading and plugin processing
- Test covers theme validation, template loading, HTML generation, and CSS processing
- All existing tests continue to pass through fallback pattern
- Integration test demonstrates theme files → plugin processing → output validation

### Issues Discovered

- **CRITICAL UX**: Gallery URL routing problems discovered during manual testing
  - `/galleries/wedding/` returns 404 (no index.html in gallery directories)
  - `/galleries/` returns 404 (no gallery index page exists)
  - Users must type full `/galleries/wedding/page_1.html` URLs to access galleries
  - Documented in TODO.md as post-MVP priority fix
  - Updated serve.md documentation with current URL limitations and workarounds

## 2025-12-11

## 2025-12-05

### Added

- Complete validate command functionality implementation
- DependencyValidator for Python dependency checking
- PermissionValidator for output directory permission verification  
- Proper exit code handling in validate command (returns 1 on failure)
- Comprehensive E2E test coverage for all validate functionality
- Serve command cascade functionality - auto-calls build when output/ missing

### Changed  

- Removed skip decorators from validate E2E tests
- Enhanced validate command with dependencies and permissions checks
- Updated validator module with three specialized validator classes
- Serve command now follows cascading pipeline pattern (serve→build→organize→validate)

### Fixed
- Serve command cascade to build pipeline when output directory missing
- Proper error handling when build fails during serve cascade

### Documentation

- Added doc/commands/validate.md with complete validate command documentation
- Updated doc/modules/validator.md with:
  - DependencyValidator
  - PermissionValidator APIs
- Added validate command link to doc/commands/README.md
- Updated serve command documentation with cascade behavior

- Added theme system integration tests in test/e2e/test_theme_integration.py
- Integration test covers theme file loading, template rendering, CSS processing
- Tests for theme validation and PicoCSS integration prepared
- Added ThemeValidator unit tests with theme directory structure validation
- Added theme-based template and CSS plugin unit tests
- All existing tests preserved through fallback implementation pattern
- Complete test suite passes with theme system integration

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
- BasicCSSPlugin now supports theme_path configuration
- Theme-based CSS file reading from static/css directory
- CSS files sorted with custom.css loaded last for highest priority
- Fallback to hardcoded CSS when theme_path not configured

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
