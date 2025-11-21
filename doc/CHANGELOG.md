# Changelog

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
