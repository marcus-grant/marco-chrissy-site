# Changelog

## 2025-11-19

* Implement Galleria plugin system foundation
  - Create base plugin interface with abstract BasePlugin class
  - Add plugin system directory structure (galleria/plugins/)
  - Implement abstract methods for plugin name and version properties
  - Add comprehensive unit tests for plugin interface contracts (6 tests)
  - Create organized test structure (e2e/, integration/, unit/ directories)
  - Follow TDD approach with failing tests first, then implementation

## 2025-11-18

* Reorganize Galleria module documentation into hierarchical structure
  - Create doc/modules/galleria/ subdirectory for detailed module docs
  - Add processor.md with comprehensive API documentation
  - Add serializer.md with data model and loader documentation
  - Simplify galleria-structure.md to be overview only
  - Update modules/README.md to link to galleria subdirectory
  - Follow one-level linking rule for documentation hierarchy
* Implement Galleria processor module using TDD approach
  - Add ImageProcessor class with process_image method
  - Implement 400x400 square thumbnail generation with center crop strategy
  - Add WebP format conversion with configurable quality settings
  - Implement naive thumbnail caching using mtime comparison
  - Add error handling for corrupted or missing images
  - Implement progress reporting for large photo collections
  - Add comprehensive integration and unit test coverage (17 tests)
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
