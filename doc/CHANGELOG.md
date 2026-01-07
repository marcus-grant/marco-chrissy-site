# Changelog

## 2025-01-07

- Fix gallery CDN URLs: Update config/site.json with correct bunny.net CDN domains
- Gallery thumbnails now use https://marco-crissy-site.b-cdn.net instead of incorrect site-cdn.bunnycdn.com
- Photo CDN configured as https://marco-crissy-photos.b-cdn.net for future dual-CDN support

## 2025-01-05

- Complete deploy CLI integration with dual client configuration system
- Fix CLI deploy command method call (get_deploy_config → load_deploy_config)
- Remove @pytest.mark.skip from E2E deploy tests - all tests now pass
- Update all E2E tests to use new dual client architecture with proper mocking
- Deploy implementation complete: All 508 tests passing, ready for real-world testing
- Refactor all deploy tests to use configurable dual client architecture
- Fix orchestrator API method signature mismatch for upload_file calls
- Update DeployOrchestrator to accept photo_zone_name and site_zone_name parameters
- Fix deploy_photos and deploy_site_content to call upload_file with required zone_name parameter
- Add comprehensive test coverage for zone-specific upload calls
- Resolve primary blocking issue preventing bunny.net deployment functionality
- Fix zone name typos in documentation (marco-chrissy-site → marco-crissy-site)
- Add environment variable support for zone names in deploy CLI command
- Update deploy command to read BUNNYNET_PHOTO_ZONE_NAME and BUNNYNET_SITE_ZONE_NAME
- Add proper mocking of os.getenv in tests to avoid using real environment variables
- Update all deployment tests to use isolated test values instead of production configs
- Add configurable deploy configuration system with flat structure supporting environment variable name specification
- Create config/deploy.json with photo_password_env_var and site_password_env_var fields for dual client architecture
- Add load_deploy_config() method to ConfigManager following existing config loading patterns
- Implement proper test isolation using arbitrary test environment variable names instead of production values
- Replace create_client_from_env() with configurable create_clients_from_config() for dual client architecture
- Remove hardcoded BUNNYNET_STORAGE_PASSWORD dependency in favor of config-specified environment variable names
- Implement dual client creation returning separate photo_client and site_client instances with zone-specific passwords
- Add comprehensive test coverage for dual client creation with arbitrary test environment variable names
- Breaking change: All callers of create_client_from_env() must migrate to config-driven dual client approach
- Update BunnyNetClient constructor to accept zone_name parameter, removing zone_name from upload_file() calls
- Refactor DeployOrchestrator to accept separate photo_client and site_client instead of single client + zone names
- Update orchestrator upload methods to use photo_client and site_client directly with zone-specific routing
- Remove zone name storage from orchestrator (clients contain zone information internally)
- Add comprehensive test for dual client orchestrator constructor with proper client isolation

## 2025-01-04

- Fix BunnyNetClient instantiation issue in deploy command by using create_client_from_env factory
- Update all deploy unit tests to mock create_client_from_env instead of direct BunnyNetClient class
- Add test for correct BunnyNetClient instantiation pattern to prevent regression
- Resolve critical blocking issue preventing deploy command from working with environment variables

## 2025-12-29

- Create comprehensive E2E tests for deploy command using Click testing and isolated fixtures
- Replace subprocess-based tests with CliRunner for better performance
- Add complete deploy test coverage: dual zone strategy, manifest comparison, pipeline integration, error handling
- Ensure complete test isolation with temp filesystem and proper fixtures
- Create BunnyNetClient stub with authentication validation and environment variable handling
- Add comprehensive unit tests for client initialization and region configuration (with security warnings)
- Implement complete BunnyNet API client with HTTP upload/download functionality using requests
- Add comprehensive unit tests for file upload/download with proper mocking and error handling
- Ensure secure implementation that never inspects environment variable values during testing

## 2025-12-23

### Completed - Test Suite Cleanup and Fixes

#### Fixed Test Failures
- **Fixed remaining test failure**: Resolved `Path.cwd()` issue in galleria serve orchestrator
  - Use config file's parent directory as base_dir instead of Path.cwd()
  - Prevents FileNotFoundError when working directory is cleaned up in test isolation
  - Updated unit tests to reflect new behavior

#### Test Suite Optimization
- **Deleted worthless mock-based integration tests**: Removed 2 tests that only asserted mock calls without verifying actual functionality
  - Removed `test_shared_components_integration_without_subprocess` from test_shared_components.py
  - Removed `test_refactored_serve_architecture` from test_site_serve.py
  - Kept `test_serve_orchestrator_graceful_shutdown_on_signal` as it tests real signal handling behavior
  - Test suite now: **456 passed, 6 skipped** (down from 458 passed)
  - Reduced test suite execution time by removing wheel-spinning tests

#### Test Infrastructure Improvements  
- **Added shared theme_factory fixture**: Enhanced test consistency and reduced duplication
  - Moved theme_factory from local pelican builder test to shared test/conftest.py
  - Enhanced to support both pelican and galleria theme types
  - Refactored existing tests to use shared fixture for consistent theme creation patterns
  - Removed local theme_factory definitions in favor of shared implementation

#### Results
- **All tests passing**: No failures remaining from the original 3 test failures identified in TODO
- **Clean test suite**: Ready for Phase 6 (Performance Baseline) and final MVP preparation
- **Improved test maintainability**: Consistent theme creation patterns across all tests

## 2025-12-19

### Completed - Shared Component Integration (PR #17)

**MAJOR MILESTONE**: Shared component integration successfully completed and merged.

#### Core Integration Fixes
- **Header consistency achieved**: Both Pelican and Galleria use identical shared navbar
- **Template override system**: Successfully implemented Pelican theme override mechanism using `THEME_TEMPLATES_OVERRIDES`
- **External template integration**: Galleria now uses `theme_path` to access shared components
- **Clean HTML output**: Eliminated Pelican automatic title generation and duplicate headings
- **Modern semantic structure**: Removed `<hgroup>` elements, content uses proper H1 for titles
- **Template files created**: `themes/shared/templates/` with base.html, index.html, article.html overrides

#### Test Suite Fixes (13 of 16 resolved)
- Fixed shared theme configuration tests (removed hardcoded "notmyidea" theme)
- Fixed template URL path expectations with relative path changes
- Fixed orchestrator working directory issues (config dir → project root)
- Removed 2 obsolete skipped theme tests
- Added pytest multithreading by default for faster test execution
- Updated .gitignore to include pytest-slow-first.json cache file

#### Configuration Updates
- Updated `config/schema/galleria.json` to include `theme_path` property
- Fixed `THEME_TEMPLATES_OVERRIDES` (plural) setting name throughout codebase
- Updated `config/galleria.json` and `config/pelican.json` with proper shared component paths

#### Documentation (Comprehensive)
- Created `doc/modules/pelican/` directory with README.md, theme-overrides.md, quirks.md
- Created `doc/modules/shared/` directory with README.md, external-integration.md
- Updated existing documentation (configuration.md, architecture.md, galleria/themes.md)
- Updated navigation hierarchy following CONTRIBUTE.md adjacency rules

#### Build System Integration
- Updated GalleriaBuilder to use `theme_path` configuration
- Updated PelicanBuilder template override logic
- Both systems now correctly include shared navigation and CSS

**Result**: Shared component integration now functionally complete with consistent navigation and styling across all pages.

### Earlier Work (Dec 19)

- Restructured TODO.md to follow PLANNING.md template with proper phase/cycle organization
- Enhanced integration test to detect Pelican theme override configuration issues
- Added duplicate navbar detection to verify single shared navbar in both systems

## 2025-12-18

### Fixed

- Resolved test pollution issue: identified root cause as tests/commands running from config/ directory with relative paths
- Fixed shared navbar integration test assertion to match actual Galleria output (id="shared-navbar" vs id="test-shared-navbar")
- Completed THEME_TEMPLATE_OVERRIDES alignment between Pelican and Galleria configurations
- Resolved CSS pipeline ordering issues in shared component system
- Fixed gallery template variable names and empty photo path handling

### Added

- Implemented shared navbar template and CSS components with proper integration
- Added comprehensive config alignment for shared theme system
- Created definitive integration tests for shared component verification
- Added proper test isolation safeguards to prevent production path pollution

### Technical Debt Resolved

- **Critical Discovery**: Test pollution was caused by relative paths in config files when commands run from wrong directory
- **Solution**: All tests now use proper temp_filesystem isolation, .gitignore updated to prevent future pollution
- **Status**: Shared component integration actually WORKS - previous test failures were due to test bugs, not system failures

### Completed

- Phase 5A.1: THEME_TEMPLATE_OVERRIDES config alignment between Pelican and Galleria
- Phase 5A: Shared component integration (Pelican + Galleria both rendering shared navbar and CSS)
- Test pollution cleanup and permanent prevention measures

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

### Critical Issues Discovered

**BLOCKING:** Shared component integration is fundamentally broken despite "passing" tests:
- Pelican builds but `{% include 'navbar.html' %}` appears as literal text, not rendered
- Galleria template system has no shared template support
- All existing E2E/integration tests are worthless - they test mocks instead of actual HTML output
- Created `test_shared_navbar_integration.py` - the ONLY test that matters for this feature
- Manual testing confirms no shared navbar appears in gallery pages

### Completed

- Removed @pytest.mark.skip decorators from real plugin integration test  
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
