# Changelog

## 2025-11-18

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
