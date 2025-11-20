# Changelog

## 2025-11-20

* Implement CLI entry point and argument parsing with TDD methodology
  - Add galleria/__main__.py for `python -m galleria` support
  - Implement basic argument parsing for --config, --output, --verbose flags
  - Add configuration file loading and validation with pagination logic
  - Generate gallery files based on calculated page counts and collection data
  - Follow proper TDD red-green-refactor cycle driven by E2E test failures
* Fix pagination calculation logic to use proper mathematical formula
  - Change from counting created pages to calculating pages needed upfront
  - Use ceil(num_photos / page_size) formula for both pagination plugins
  - Handle empty collections correctly (create one empty page)
  - Add comprehensive unit tests covering all pagination math edge cases
  - Fix both BasicPaginationPlugin and SmartPaginationPlugin calculation logic
* Add CLI generate command E2E tests with comprehensive coverage
  - Create failing E2E tests for `galleria generate --config --output --verbose` command
  - Test complete CLI workflow: argument parsing, config loading, plugin execution
  - Test error handling for missing config files, invalid JSON, missing arguments
  - Cover realistic usage scenarios with NormPic manifests and gallery generation
  - Foundation ready for CLI implementation following TDD red-green-refactor cycle
* Complete real plugin E2E integration workflow
  - Fix plugin registry integration issues with tuple/dict stage configuration API
  - Fix data contract validation between plugins with backward-compatible config access
  - Resolve config pattern mismatch between nested (E2E) and direct (unit) config access
  - All plugins now support both config patterns: nested stage-specific and direct access
  - E2E test for complete 5-stage plugin pipeline now passes (Provider → Processor → Transform → Template → CSS)
  - Real plugin integration working end-to-end with proper pagination and file generation

## 2025-11-19

* Complete Template, CSS, and Pagination plugin implementations with TDD methodology
  - Implement TemplatePlugin with BasicTemplatePlugin for HTML generation
  - Add semantic HTML5 gallery pages with pagination navigation support
  - Support configurable themes (minimal, elegant, modern) and layouts (grid, flex)
  - Implement CSSPlugin with BasicCSSPlugin for comprehensive stylesheet generation
  - Generate responsive CSS with light/dark/auto themes and mobile breakpoints
  - Support modular CSS files (gallery.css, theme.css, responsive.css)
  - Implement PaginationPlugin with BasicPaginationPlugin and SmartPaginationPlugin
  - Add intelligent page balancing to avoid small last pages
  - Support configurable page sizes (1-100) with validation and metadata tracking
  - Add 28 comprehensive unit tests covering all plugin interfaces and error scenarios
  - Create template-plugins.md documentation with usage examples and API reference
  - Update plugin-system.md with concrete plugin implementations catalog
  - Follow strict TDD methodology: 7 small commits (tests → implementation → docs)
  - Maintain commit size limits: all commits under 365 lines each
* Complete plugin system foundation with all 5 interfaces implemented
  - TemplatePlugin, CSSPlugin, and pagination transforms now fully functional
  - E2E test demonstrates complete Provider → Processor → Transform → Template → CSS pipeline
  - Plugin system ready for orchestration and complete workflow implementation
  - Test count progression: 170+ tests covering entire plugin ecosystem

* Convert processor to ThumbnailProcessorPlugin with full TDD methodology
  - Implement ThumbnailProcessorPlugin following ProcessorPlugin interface contract
  - Convert existing galleria/processor/image.py logic to plugin system architecture
  - Create comprehensive E2E integration test for real provider-to-processor pipeline
  - Add 11 unit tests covering success, validation, error handling, and caching scenarios
  - Add 5 integration tests covering plugin contract compliance and provider integration
  - Achieve target test count of 155-165 tests (16 new tests added to foundation)
  - Maintain full backward compatibility with legacy ImageProcessor API
* Implement complete ProviderPlugin to ProcessorPlugin pipeline integration
  - Process ProviderPlugin output format and add thumbnail_path, thumbnail_size fields
  - Preserve all ProviderPlugin data (photos, metadata, collection info) through processing
  - Implement intelligent caching with should_process() logic from existing processor
  - Handle individual photo errors gracefully without stopping batch processing
  - Support configuration options: thumbnail_size, quality, use_cache, output_format
* Update documentation to reflect processor plugin system implementation
  - Revise doc/modules/galleria/processor.md with plugin system integration
  - Add comprehensive plugin usage examples with PluginContext configuration
  - Document ProcessorPlugin contract format and data preservation guarantees
  - Add migration guidance for existing ImageProcessor code vs new plugin system
  - Mark processor plugin implementation as completed in architecture documentation

## 2025-11-19

* Convert serializer to NormPicProviderPlugin with full TDD methodology
  * Implement NormPicProviderPlugin following ProviderPlugin interface contract
  * Convert existing galleria/serializer/loader.py logic to plugin system architecture  
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
  * Update doc/provider-architecture.md with concrete NormPicProviderPlugin examples  
  * Add migration guidance for existing code vs new plugin system usage
  * Document plugin output format and ProviderPlugin interface compliance
  * Mark NormPic provider implementation as completed (was previously future work)

## 2025-11-19

* Complete plugin interface integration and E2E validation
  * Validate E2E test from Commit 1d works with all 5 implemented interfaces
  * Confirm complete Provider → Processor → Transform → Template → CSS pipeline
  * Verify all 130 tests continue passing with full interface integration
  * Update plugin-system.md with interface implementation status
  * Plugin system foundation now 100% complete and ready for concrete implementations

## 2025-11-19

* Complete Template and CSS plugin interfaces with TDD methodology
  * Add failing integration tests for Transform ↔ Template ↔ CSS interaction
  * Implement TemplatePlugin interface with generate_html() abstract method
  * Implement CSSPlugin interface with generate_css() abstract method  
  * Add 15 comprehensive unit tests for interface contracts and validation
  * Update plugin-system.md documentation with detailed interface specs
  * Follow strict TDD: red → green → refactor methodology
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

## 2025-11-19

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
  * Test progression: 91 → 105 tests (+14 new tests)
* Add Transform plugin interface with TDD methodology
  * Create failing integration tests for Processor ↔ Transform interaction (3 tests)
  * Define TransformPlugin interface with transform_data() abstract method
  * Support pagination, sorting, and filtering data transformation operations
  * Add comprehensive unit tests for interface validation (7 tests)
  * Update plugin-system.md documentation with Transform interface specification
  * Test progression: 105 → 115 tests (+10 new tests)

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
