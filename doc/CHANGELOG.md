# Changelog

## 2025-11-28

### Serve Command Implementation Planning

* **STARTED: Serve command implementation planning and task breakdown**
  * Added comprehensive serve command implementation tasks to doc/TODO.md Phase 3
  * Created step-by-step TDD workflow plan for Galleria serve (standalone) and Site serve (coordinated)
  * Defined module organization: galleria/orchestrator/serve.py, galleria/server/, galleria/util/watcher.py
  * Added future enhancement tasks: smart rebuilds, configurable paths, URL pattern documentation
  * Planned proxy architecture: /galleries/* → Galleria, /pics/* → static files, else → Pelican
  * Each task specifies exact implementation, testing, documentation, and commit workflow
  * Ready to begin implementation following nested TDD pattern (E2E → unit tests → implementation)

* **COMPLETED: Development dependencies and planning documentation**
  * Added watchdog>=3.0.0 to pyproject.toml dev dependencies for file watching functionality
  * Documented planning process in doc/CONTRIBUTE.md to streamline future feature planning
  * Established task structure format with concrete file paths and pre-commit workflows
  * All dependencies installed and tests passing (315 passed, 9 skipped)

* **PLANNED: Replace existing serve command with proper architecture**
  * Updated TODO.md to replace old serve implementation with modular design
  * Plan includes removal of existing serve command and tests
  * New implementation will follow orchestrator pattern with proper separation
  * Module organization: galleria/orchestrator/serve.py, galleria/server/, galleria/util/watcher.py

## 2025-11-27

### Build Command Integration FIXED + Build Orchestrator Refactoring COMPLETED + Documentation Updates

* **COMPLETED: Pelican integration issues resolved**
  * Fixed build command Pelican configuration to use proper pelican.settings.configure_settings()
  * Updated pelican.json schema with all required Pelican settings (THEME, IGNORE_FILES, DELETE_OUTPUT_DIRECTORY, etc.)
  * Use DEFAULT_CONFIG.copy() as base and override with our specific settings
  * Added proper content directory creation and theme validation
  * Core Pelican functionality now working - E2E test shows successful build pipeline
  * Galleria integration remains solid with direct module imports and plugin system

* **COMPLETED: Build orchestrator refactoring successfully finished**
  * Problem SOLVED: Build command was "god function" (195 lines, multiple responsibilities)
  * Solution IMPLEMENTED: Extracted business logic into dedicated orchestrator and builder classes
  * Results ACHIEVED: 
    - 77% code reduction: Build command reduced from 195 to 45 lines
    - Perfect testability: Mock 1 class instead of 4+ dependencies per test
    - Full reusability: BuildOrchestrator callable from non-CLI contexts
    - Single responsibility: Each class has one clear job
    - Maintainability: Business logic completely separated from CLI presentation
  * Implementation: 7-commit incremental refactoring using strict TDD approach
    - Commit 2: ConfigManager - Unified config loading (5 tests, 100% coverage)
    - Commit 3: GalleriaBuilder - Galleria pipeline extraction (3 tests, 100% coverage)
    - Commit 4: PelicanBuilder - Pelican generation extraction (3 tests, 100% coverage)  
    - Commit 5: BuildOrchestrator - Main coordination class (3 tests, 100% coverage)
    - Commit 6: Refactored build command - Simple orchestrator call (-157 lines deleted)
    - Commit 7: E2E test updated and passing - Complete workflow verified
    - Commit 8: Unit test fixes - Updated all 9 build unit tests for orchestrator pattern (0 skipped, 9 passing)

* **Commit 1 COMPLETED: Build module structure and exceptions**
  * Created build/ package for orchestration functionality
  * Added BuildError base exception with ConfigError, GalleriaError, PelicanError subclasses
  * Implemented proper exception hierarchy with inheritance and chaining support
  * Full unit test coverage for exception behavior

* **COMPLETED: Comprehensive documentation updates for orchestrator refactoring**
  * Created complete build module documentation (doc/modules/build/)
    - BuildOrchestrator usage and API reference
    - ConfigManager unified config loading guide  
    - GalleriaBuilder and PelicanBuilder integration patterns
    - Build exception hierarchy documentation
  * Updated architecture documentation (doc/architecture.md)
    - Added Build Orchestrator Architecture section with benefits and structure
    - Updated directory structure to reflect implemented build module
    - Removed outdated "broken" status and added "completed" achievements
  * Updated workflow documentation (doc/workflow.md) 
    - Added orchestrator pattern benefits (77% code reduction, better testing)
    - Updated build command integration section for new architecture
  * Updated testing documentation (doc/testing.md)
    - Added Build Module Testing Patterns section
    - Documented simplified mocking (1 orchestrator vs 4+ dependencies)
    - Added before/after testing pattern examples
  * Updated TODO.md
    - Removed completed orchestrator and test fixing tasks
    - Cleaned up outdated configuration architecture tasks  
    - Focused next immediate tasks on serve command implementation

### Previous Build Command Integration Issues (RESOLVED)

* **RESOLVED: Build command broken after galleria integration attempt**
  * Galleria integration works: successfully uses PipelineManager, plugin registration, direct imports
  * **Pelican integration FIXED**: All configuration issues resolved
  * All required Pelican settings now handled properly
  * Unit tests simplified with better mocking pattern (mock fewer dependencies)
  * E2E test core functionality working (minor test assertions still being refined)
  * **STATUS: Core functionality working, refactoring in progress for better architecture**

### Unified Configuration System Completion

* **Complete JSON schema validation for all config types**
  * Add comprehensive unit tests for pelican.json and galleria.json schema validation
  * Create config/schema/pelican.json with required fields: theme, site_url, author, sitename
  * Create config/schema/galleria.json designed for extraction-ready galleria package
  * Include optional fields like timezone, default_lang for pelican and thumbnail settings for galleria
  * All schemas follow JSON Schema draft-07 standard with proper validation rules

* **Enhanced ConfigValidator with schema validation**
  * Update ConfigValidator to use JsonConfigLoader for actual content validation
  * Replace simple file existence checks with comprehensive schema validation  
  * Load schemas from config/schema/ directory and validate config content against them
  * Maintain backward compatibility when schema files are missing
  * Provide detailed error messages for validation failures with field context
  * Add unit tests for both valid and invalid config validation scenarios

* **Build command integration with unified config system**
  * Update cli/commands/build.py to load site.json and galleria.json configurations
  * Replace hard-coded galleria.generate() calls with proper CLI subprocess invocation
  * Use config-driven output paths from site.json for idempotent behavior checks
  * Create temporary galleria config files for CLI integration while maintaining extraction-ready design
  * Integrate with galleria CLI using proper config file format matching schemas

* **Complete E2E test validation and system integration**
  * Remove @pytest.mark.skip from all config integration E2E tests
  * Fix config formats in tests to match implemented JSON schemas
  * Add schema file copying to temp filesystems in all E2E test scenarios
  * Update galleria config format from pipeline structure to manifest_path/output_dir format
  * All 4 E2E config integration tests now pass: valid configs, schema errors, missing files, JSON corruption
  * Unified configuration architecture fully functional and comprehensively tested

## 2025-11-26

### Phase 2 Build Command Implementation

* **Complete build command TDD implementation**
  * Create comprehensive E2E test with fake filesystem and BeautifulSoup HTML validation
  * Add 8 unit tests covering organize cascade, galleria/pelican integration, error handling
  * Implement cli/commands/build.py following organize command patterns
  * Use direct Python module imports (galleria.generate(), pelican.Pelican()) not CLI subprocess
  * Add proper error handling and user progress output for each pipeline stage

* **Test infrastructure improvements**
  * Centralize fake image generation into shared fake_image_factory fixture
  * Support both raw JPEG bytes (NormPic tests) and PIL images (Galleria tests)
  * Add BeautifulSoup dependency for HTML content validation in E2E tests
  * Update existing organize tests to use centralized image fixtures

* **Development workflow documentation**
  * Add mandatory Code Quality Workflow section to CONTRIBUTE.md
  * Document critical ruff → test → commit sequence to prevent logic breakage
  * Update Testing Requirements with ruff-first workflow references
  * Emphasize always testing after automatic formatting to catch edge cases

## 2025-11-25

### Phase 2 Organize Command Implementation

* **Real NormPic integration with direct Python imports**
  * Add normpic as git dependency with direct references support
  * Replace NormPicOrganizer stub with real normpic module integration
  * Implement actual photo organization: ~/Pictures/wedding/full → output/pics/full
  * Support proper NormPic API: organize_photos() with manifest generation

* **Configuration loading and path management**
  * Add config loading from config/normpic.json with sensible fallback defaults
  * Support constructor parameter overrides for testing and flexibility
  * Set production paths: source from ~/Pictures/wedding/full, dest to output/pics/full
  * Handle missing config files gracefully with default configuration

* **Comprehensive organize E2E testing**
  * Create fake JPEG files with minimal EXIF structure for realistic testing
  * Verify symlink creation with actual NormPic filename patterns containing collection name
  * Parse and validate manifest.json content with comprehensive photo entry verification
  * Test complete source→dest path mapping and symlink integrity
  * Use fixture system for config setup with temporary filesystem paths
  * Unskip test_organize_generates_manifest with full end-to-end verification

* **Enhanced command output and error reporting**
  * Update organize command to display processed photo counts and manifest paths
  * Provide meaningful error messages for missing directories and NormPic failures
  * Return structured results with success status, error details, and processing metrics

## 2025-11-21

### Phase 2 Architecture Planning

* **4-stage idempotent pipeline design**
  * Planned validate → organize → build → deploy command structure
  * Each stage calls predecessors automatically if needed
  * Lazy execution to avoid unnecessary work

* **Plugin-based Pelican integration strategy**
  * PelicanTemplatePlugin approach to maintain Galleria extractability
  * Shared Jinja2 templates for consistent navigation/styling
  * Site-specific logic stays in site repo through plugin system

* **Project structure planning**
  * Root-level modules: cli/, validator/, build/, deploy/, serializers/
  * Separate JSON configs with schema validation
  * Dual CDN output strategy (photos vs site content)

* **Documentation updates**
  * Updated TODO.md with detailed Phase 2 breakdown
  * Added architecture documentation for planned pipeline
  * Established feature branch workflow for Phase 2 development

### Phase 2 CLI Implementation Start

* **Test structure setup**
  * Created test/e2e/ and test/unit/ directories for site functionality
  * Updated TODO.md to specify test locations for all future development
  * Established nested TDD workflow with clear test organization

* **Basic CLI command structure**
  * Implemented Click-based CLI with main entry point (cli/main.py)
  * Created minimal validate, organize, build, deploy command stubs
  * Registered site command in pyproject.toml for uv run site access
  * All basic command discovery E2E tests pass (5/6 tests passing)
  * One test remains skipped for idempotent cascading behavior (Phase 2 MVP milestone)

### Phase 2 Validate Command Implementation

* **Reusable test infrastructure**
  * Created comprehensive fixture system in test/conftest.py
  * Added temp_filesystem, file_factory, directory_factory fixtures
  * Implemented config_file_factory with defaults for all config types
  * Added full_config_setup fixture for complete test environments
  * All fixtures validated with 6 dedicated tests

* **Validate command functionality**
  * Implemented validator/config module with ConfigValidator class
  * Added ValidationResult dataclass for structured error reporting
  * Created config file validation for site.json, normpic.json, pelican.json, galleria.json
  * Unit tests for config validation (4 tests passing)
  * E2E test for validate command using temporary filesystem (1 test passing)
  * Command provides meaningful error messages for missing config files

## 2025-11-20

### Serve Command Implementation (Phase 1.5)

* **Complete development server implementation**
  * Add `galleria serve` command with comprehensive CLI argument parsing
  * Implement generate-then-serve workflow with automatic gallery generation
  * Create HTTP development server with proper MIME type handling and error responses
  * Support configurable port, host binding, and verbose logging options

* **Hot reload and file watching functionality**  
  * Monitor configuration files and NormPic manifests for changes
  * Automatically regenerate gallery when watched files are modified
  * Provide real-time development workflow with browser refresh capability
  * Support `--no-watch` flag to disable file monitoring for production-like testing

* **Comprehensive E2E testing for serve command**
  * Test complete serve workflow from generation through HTTP serving
  * Validate hot reload functionality with real file modifications
  * Test server startup, file serving, and graceful shutdown scenarios
  * Cover error handling for missing configs, port conflicts, and invalid arguments

* **Production-ready development server features**
  * Root URL redirect to main gallery page (page_1.html)
  * CORS headers for local development and API testing
  * Port reuse and proper socket cleanup to prevent "address in use" errors
  * Comprehensive error handling with meaningful user messages
  * Support for `--no-generate` flag to serve existing galleries without regeneration

### Documentation Completion & Enhancement

* **Comprehensive E2E workflow documentation**
  * Create complete end-to-end workflow guide covering NormPic -> Galleria -> deployment
  * Document production configuration examples for common use cases
    * *(wedding, portfolio, events)*
  * Add integration guides for static site generators (Pelican, manual deployment)
  * Document E2E testing approach with real image processing validation

* **Plugin system documentation updates**
  * Update plugin implementation status to reflect completed work
  * Mark all core plugins as implemented
    * *(Provider, Processor, Transform, Template, CSS)*
  * Remove outdated "future" annotations for completed functionality
  * Update plugin architecture documentation with current capabilities

* **Documentation hierarchy improvements**
  * Fix broken links in main documentation README
  * Remove references to non-existent documentation files
  * Add workflow guide to main documentation index
  * Clean up outdated TODO entries that duplicate completed work

### Code Quality & Maintenance Improvements

* **Exception handling improvements**
  * Add proper exception chaining for better error traceability
  * Improve debugging capabilities by preserving original exception context

* **Code formatting and style cleanup**
  * Remove trailing whitespace across galleria module files
  * Fix blank line formatting in pipeline, plugins, and registry files
  * Standardize formatting in CSS, template, and pagination plugins

* **Test quality improvements**
  * Replace assert False patterns with proper test assertions
  * Fix B011 linting violations in plugin registry tests
  * Improve test readability and maintainability

* **Test formatting cleanup**
  * Remove trailing whitespace from all unit test files
  * Add proper final newlines to test files
  * Standardize test file formatting across pagination, CSS, and template tests

* **Project metadata updates**
  * Update pyproject.toml with latest project configuration
  * Ensure linting and formatting standards are properly configured

### Phase 1 Completion: Galleria CLI E2E Validation (Commit 8e)

* **Complete CLI generate command E2E validation**
  * Fix critical file writing issue in CLI:
    * HTML and CSS files now properly written to disk
  * Add missing file writing logic to galleria/**main**.py for HTML and CSS output
  * CLI now executes complete pipeline and persists all generated content
    * *(HTML, CSS, thumbnails)*
  * Update all CLI unit tests to use correct file data structure format
* **Fix E2E test image processing issues**
  * Replace invalid minimal JPEG headers with
    proper PIL-generated JPEG images in tests
  * Create valid 100x100 RGB test images using PIL for reliable thumbnail processing
  * Fix fake filesystem test to create real JPEG data instead of
    header-only mock files
  * All E2E tests now use realistic photo data that passes through actual image processing
* **Resolve all skipped tests and achieve complete test coverage**
  * Fix fake filesystem CLI test by creating proper JPEG data and removing skip marker
  * Fix error handling test expectations to match graceful error handling behavior
    *(success with logged errors)*
  * Eliminate all skipped tests: 239/239 tests now passing with 0 skipped
  * Complete test suite validates entire CLI workflow end-to-end
* **CLI fully functional for production use**
  * [x] Loads and validates configuration files with comprehensive error messages
  * [x] Executes complete plugin pipeline:
    * *provider -> processor -> transform -> template -> css*
  * [x] Generates and writes:
    * *HTML pages, CSS stylesheets, and WebP thumbnails to disk*
  * [x] Provides verbose progress reporting and graceful error handling
  * [x] Supports output directory override and all CLI options documented
  * [x] Ready for Phase 2 site integration workflow

### Previous Commit 8 Work (CLI Implementation)

* Implement CLI entry point and argument parsing with TDD methodology
  * Add galleria/**main**.py for `python -m galleria` support
  * Implement basic argument parsing for --config, --output, --verbose flags
  * Add configuration file loading and validation with pagination logic
  * Generate gallery files based on calculated page counts and collection data
  * Follow proper TDD red-green-refactor cycle driven by E2E test failures
* Fix pagination calculation logic to use proper mathematical formula
  * Change from counting created pages to calculating pages needed upfront
  * Use ceil(num_photos / page_size) formula for both pagination plugins
  * Handle empty collections correctly (create one empty page)
  * Add comprehensive unit tests covering all pagination math edge cases
  * Fix both BasicPaginationPlugin and SmartPaginationPlugin calculation logic
* Add CLI generate command E2E tests with comprehensive coverage
  * Create failed E2E test for `galleria generate --config --output --verbose`
  * Test complete CLI workflow: argument parsing, config loading, plugin execution
  * Test error handling for missing config files, invalid JSON, missing arguments
  * Cover realistic usage scenarios with NormPic manifests and gallery generation
  * Foundation ready for CLI implementation following TDD red-green-refactor cycle
* Complete real plugin E2E integration workflow
  * Fix plugin registry integration issues with tuple/dict stage configuration API
  * Fix data contract validation for plugins w/ back-compatible config access
  * Resolve cfg pattern mismatch between nested (E2E) & direct (unit) cfg access
  * All plugins now support both config patterns:
    * *nested stage-specific and direct access*
  * E2E test for complete 5-stage plugin pipeline now passes
    * *(Provider -> Processor -> Transform -> Template -> CSS)*
  * Real plugin integration working end-to-end with proper pagination and file generation

## 2025-11-19

* Complete Template, CSS, and Pagination plugin implementations with TDD methodology
  * Implement TemplatePlugin with BasicTemplatePlugin for HTML generation
  * Add semantic HTML5 gallery pages with pagination navigation support
  * Support configurable themes (minimal, elegant, modern) and layouts (grid, flex)
  * Implement CSSPlugin with BasicCSSPlugin for comprehensive stylesheet generation
  * Generate responsive CSS with light/dark/auto themes and mobile breakpoints
  * Support modular CSS files (gallery.css, theme.css, responsive.css)
  * Implement PaginationPlugin with BasicPaginationPlugin and SmartPaginationPlugin
  * Add intelligent page balancing to avoid small last pages
  * Support configurable page sizes (1-100) with validation and metadata tracking
  * Add 28 comprehensive unit tests covering all plugin interfaces and error scenarios
  * Create template-plugins.md documentation with usage examples and API reference
  * Update plugin-system.md with concrete plugin implementations catalog
  * Follow strict TDD methodology: 7 small commits (tests -> implementation -> docs)
  * Maintain commit size limits: all commits under 365 lines each
* Complete plugin system foundation with all 5 interfaces implemented
  * TemplatePlugin, CSSPlugin, and pagination transforms now fully functional
  * E2E test demonstrates complete pipeline:
    * *Provider -> Processor -> Transform -> Template -> CSS pipeline*
  * Plugin system ready for orchestration and complete workflow implementation
  * Test count progression: 170+ tests covering entire plugin ecosystem

* Convert processor to ThumbnailProcessorPlugin with full TDD methodology
  * Implement ThumbnailProcessorPlugin following ProcessorPlugin interface contract
  * Convert existing galleria/processor/image.py logic to plugin system architecture
  * Create comprehensive E2E integration test for real provider-to-processor pipeline
  * Add 11 unit tests covering success, validation, error handling, and caching scenarios
  * Add 5 integration tests covering plugin contract compliance and provider integration
  * Achieve target test count of 155-165 tests (16 new tests added to foundation)
  * Maintain full backward compatibility with legacy ImageProcessor API
* Implement complete ProviderPlugin to ProcessorPlugin pipeline integration
  * Process ProviderPlugin output format and add thumbnail_path, thumbnail_size fields
  * Preserve ProviderPlugin data (photos, metadata, collection info) by processing
  * Implement intelligent caching with should_process() logic from existing processor
  * Handle individual photo errors gracefully without stopping batch processing
  * Support configuration options: thumbnail_size, quality, use_cache, output_format
* Update documentation to reflect processor plugin system implementation
  * Revise doc/modules/galleria/processor.md with plugin system integration
  * Add comprehensive plugin usage examples with PluginContext configuration
  * Document ProcessorPlugin contract format and data preservation guarantees
  * Add migration guidance for existing ImageProcessor code vs new plugin system
  * Mark processor plugin implementation as completed in architecture documentation

* Convert serializer to NormPicProviderPlugin with full TDD methodology
  * Implement NormPicProviderPlugin following ProviderPlugin interface contract
  * Convert existing `galleria/serializer/loader.py` to plugin system architecture
  * Create comprehensive E2E integration test for real NormPic manifest loading
  * Add 10 unit tests covering success, validation, and error handling scenarios
  * Add 5 integration tests covering plugin contract compliance and backward compatibility
  * Achieve target test count of 135-140 tests (15 new tests added to foundation)
  * Maintain full backward compatibility with legacy serializer API
* Implement complete NormPic manifest to plugin format conversion
  * Convert NormPic pics array to ProviderPlugin photos contract format
  * Move NormPic fields (hash, size_bytes, mtime, camera, gps) to metadata structure
  * Preserve source_path and dest_path as top-level photo fields per contract
  * Handle optional fields (collection_description, manifest_version) appropriately
  * Implement robust error handling with PluginResult.errors structure
* Update documentation to reflect plugin system implementation
  * Revise doc/modules/galleria/serializer.md with plugin system integration
  * Update doc/provider-architecture.md w/ concrete NormPicProviderPlugin ex's
  * Add migration guidance for existing code vs new plugin system usage
  * Document plugin output format and ProviderPlugin interface compliance
  * Mark NormPic provider implementation as completed (was previously future work)

* Complete plugin interface integration and E2E validation
  * Validate E2E test from Commit 1d works with all 5 implemented interfaces
  * Confirm complete Provider -> Processor -> Transform -> Template -> CSS pipeline
  * Verify all 130 tests continue passing with full interface integration
  * Update plugin-system.md with interface implementation status
  * Plugin system foundation now 100% complete and ready for concrete implementations

* Complete Template and CSS plugin interfaces with TDD methodology
  * Add failing integration tests for Transform ↔ Template ↔ CSS interaction
  * Implement TemplatePlugin interface with generate_html() abstract method
  * Implement CSSPlugin interface with generate_css() abstract method  
  * Add 15 comprehensive unit tests for interface contracts and validation
  * Update plugin-system.md documentation with detailed interface specs
  * Follow strict TDD: red -> green -> refactor methodology
  * Achieve target test count of 130 tests (perfect progression from 115)
* Define complete plugin pipeline data contracts
  * Template input: Transform output (pages/photos data)
  * Template output: HTML files with structured markup
  * CSS input: Template output (HTML file data)  
  * CSS output: CSS files with styling + HTML passthrough
  * Maintain collection metadata flow through entire 5-stage pipeline
* Complete plugin interface foundation (5/5 interfaces implemented)
  * Provider, Processor, Transform, Template, CSS interfaces all defined
  * All interfaces tested with integration and unit test coverage
  * Ready for concrete plugin implementations in next phase

* Implement Galleria plugin system foundation
  * Create base plugin interface with abstract BasePlugin class
  * Add plugin system directory structure (galleria/plugins/)
  * Implement abstract methods for plugin name and version properties
  * Add comprehensive unit tests for plugin interface contracts (6 tests)
  * Create organized test structure (e2e/, integration/, unit/ directories)
  * Follow TDD approach with failing tests first, then implementation
* Add plugin data structures for context and results
  * Create PluginContext dataclass for input data and configuration
  * Create PluginResult dataclass for execution status and outputs
  * Add comprehensive unit tests for data structure validation (11 tests)
  * Use modern Python typing (dict/list vs Dict/List)
* Add plugin exception hierarchy using TDD approach
  * Create PluginError base exception with plugin name tracking
  * Add PluginValidationError for input/config validation failures
  * Add PluginExecutionError with original exception chaining
  * Add PluginDependencyError with missing dependencies tracking
  * Write comprehensive unit tests first, then implement (21 tests)
* Add plugin hook system and complete foundation
  * Create E2E test for complete 5-stage plugin workflow
  * Add PluginHookManager for extensibility points in pipeline
  * Implement hook registration and execution with proper ordering
  * Add comprehensive unit tests for hook system (10 tests)
  * Update plugin system documentation with hook examples
  * Create galleria/manager/ module for plugin orchestration
* Add Provider and Processor plugin interfaces with TDD methodology
  * Create failing integration tests for Provider ↔ Processor interaction (3 tests)
  * Define ProviderPlugin interface with load_collection() abstract method
  * Define ProcessorPlugin interface with process_thumbnails() abstract method
  * Implement clear data format contracts between pipeline stages
  * Add comprehensive unit tests for interface validation (11 tests)
  * Update plugin-system.md documentation with interface specifications
  * Test progression: 91 -> 105 tests (+14 new tests)
* Add Transform plugin interface with TDD methodology
  * Create failing integration tests for Processor ↔ Transform interaction (3 tests)
  * Define TransformPlugin interface with transform_data() abstract method
  * Support pagination, sorting, and filtering data transformation operations
  * Add comprehensive unit tests for interface validation (7 tests)
  * Update plugin-system.md documentation with Transform interface specification
  * Test progression: 105 -> 115 tests (+10 new tests)

## 2025-11-18

* Reorganize Galleria module documentation into hierarchical structure
  * Create doc/modules/galleria/ subdirectory for detailed module docs
  * Add processor.md with comprehensive API documentation
  * Add serializer.md with data model and loader documentation
  * Simplify galleria-structure.md to be overview only
  * Update modules/README.md to link to galleria subdirectory
  * Follow one-level linking rule for documentation hierarchy
* Implement Galleria processor module using TDD approach
  * Add ImageProcessor class with process_image method
  * Implement 400x400 square thumbnail generation with center crop strategy
  * Add WebP format conversion with configurable quality settings
  * Implement naive thumbnail caching using mtime comparison
  * Add error handling for corrupted or missing images
  * Implement progress reporting for large photo collections
  * Add comprehensive integration and unit test coverage (17 tests)
* Implement Galleria serializer module using TDD approach
* Add NormPic v0.1.0 manifest loading support
* Create Photo and PhotoCollection data models
* Add comprehensive error handling for manifest operations
* Implement E2E integration tests driving development
* Add unit tests covering all loader functionality
* Support camera metadata, GPS data, and photo collection details

## 2025-11-17

* Set up Galleria module directory structure
* Created core module directories: generator, processor, template, serializer
* Created themes directory with minimal theme structure
* Added basic theme configuration file
* Fixed pyproject.toml packaging configuration

## 2025-11-15

* Initial documentation and directory structure.
