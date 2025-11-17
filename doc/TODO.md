# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development

#### Core Functionality
- [ ] Set up Galleria module structure
  - [ ] Create galleria/generator/ directory with __init__.py
  - [ ] Create galleria/processor/ directory with __init__.py  
  - [ ] Create galleria/template/ directory with __init__.py
  - [ ] Create galleria/serializer/ directory with __init__.py
  - [ ] Create galleria/themes/ directory structure:
    - [ ] Create galleria/themes/minimal/ directory
    - [ ] Create galleria/themes/minimal/templates/ directory
    - [ ] Create galleria/themes/minimal/static/ directory
    - [ ] Create galleria/themes/minimal/config.json basic theme config
- [ ] Implement serializer module
  - [ ] Create `galleria/serializer/schemas.py`:
    - [ ] Copy NormPic's JSON schema definitions (v0.1.0)
    - [ ] Add NOTE comment: code copied from NormPic, may extract to shared package
    - [ ] Define GALLERIA_CONFIG_SCHEMA for galleria's own config
    - [ ] Add schema validation helper functions
  - [ ] Create `galleria/serializer/models.py` with dataclasses:
    - [ ] Copy ManifestData, PicData, ErrorEntry, ProcessingStatus from NormPic
    - [ ] Add NOTE comment: code copied from NormPic, may extract to shared package
    - [ ] Add GalleriaConfig dataclass (manifest_path, output_dir, thumbnail_size, etc.)
    - [ ] Ensure dataclasses match copied schema exactly
  - [ ] Create `galleria/serializer/loader.py`:
    - [ ] Implement `load_manifest(path: str) -> ManifestData`
    - [ ] Implement `load_config(path: str) -> GalleriaConfig`
    - [ ] Add JSON parsing with proper error handling
  - [ ] Create `galleria/serializer/validation.py`:
    - [ ] Implement manifest validation using copied schemas
    - [ ] Implement galleria config validation
    - [ ] Check version compatibility (support v0.1.0)
  - [ ] Create `galleria/serializer/exceptions.py`:
    - [ ] Copy relevant exception classes from NormPic
    - [ ] Add NOTE comment: code copied from NormPic, may extract to shared package
    - [ ] Add galleria-specific exceptions
  - [ ] Create tests with NOTE comments that test cases copied from NormPic
- [ ] Implement thumbnail processor
  - [ ] Create `galleria/processor/image.py` with ImageProcessor class
  - [ ] Implement `process_image(source_path, output_path, size=400)` method:
    - [ ] Load image with Pillow, handle format detection
    - [ ] Generate 400x400 square crop (center crop strategy)
    - [ ] Convert to WebP format with quality setting
    - [ ] Save to output directory with proper naming
  - [ ] Add naive thumbnail caching:
    - [ ] Check if thumbnail file exists and source file mtime is older
    - [ ] Skip processing if cache hit (simple file timestamp comparison)
    - [ ] Cache can be cleared by 'clean' command if issues arise
  - [ ] Add error handling for image processing failures
  - [ ] Implement progress reporting for large collections
- [ ] Develop plugin system using integration tests + TDD
  - [ ] Create integration tests for core plugin workflow:
    - [ ] Test manifest plugin loads NormPic manifests (v0.1.0)
    - [ ] Test processor plugin generates thumbnails from manifest data
    - [ ] Test template plugin renders pages from processed data
    - [ ] Test CSS and pagination plugins integrate properly
    - [ ] Test plugin hook points and data flow between plugins
  - [ ] Implement plugin system and default plugins:
    - [ ] Create plugin base classes and interfaces
    - [ ] Create default manifest plugin for NormPic v0.1.0
    - [ ] Create default template, CSS, pagination, and processor plugins
- [ ] Develop `generate` command using E2E tests + TDD
  - [ ] Create E2E tests for generate command:
    - [ ] Test generate command loads and orchestrates plugins correctly
    - [ ] Test default plugins work together end-to-end
    - [ ] Test plugin hook points called at correct times in workflow
  - [ ] Implement generate command that orchestrates plugin system
- [ ] Develop `serve` command using E2E tests + TDD
  - [ ] Create E2E tests for serve command:
    - [ ] Test serve calls generate (cascading command pattern)
    - [ ] Test serving generated gallery output
    - [ ] Test hot reload functionality with plugin system
  - [ ] Implement serve command that calls generate + serves locally
- [ ] Design plugin interface (foundational)
  - [ ] Define plugin hook points
  - [ ] Create plugin base class/interface
  - [ ] Design plugin discovery mechanism
  - [ ] Document plugin architecture
- [ ] Implement gallery generator
  - [ ] Orchestrate all components
  - [ ] Handle configuration
  - [ ] Create output directory structure
  - [ ] Report progress/errors
  - [ ] Integrate plugin hook points

#### CLI Interface
- [ ] Create __main__.py entry point
- [ ] Implement --config flag
- [ ] Add --verbose flag
- [ ] Add --dry-run flag
- [ ] Handle errors gracefully

#### Testing & Validation
- [ ] Set up pytest structure for Galleria
- [ ] Test manifest reader
- [ ] Test thumbnail processor
- [ ] Test HTML generation
- [ ] Test CSS generation
- [ ] Integration tests
- [ ] Test Galleria with wedding photo collection

#### Documentation
- [ ] Document Galleria configuration format
- [ ] Update Galleria architecture guide
- [ ] Write Galleria usage examples
- [ ] Document theme structure

### Phase 2: Site Structure
- [ ] Set up site project module structure
  - [ ] Create build/ directory
  - [ ] Create validation/ directory
  - [ ] Create deployment/ directory
  - [ ] Create configuration/ directory
- [ ] Implement command system
  - [ ] Create cascading command structure (validate → organize → build → deploy)
  - [ ] Implement validate command
  - [ ] Implement organize command (orchestrate NormPic)
  - [ ] Implement build command (orchestrate Galleria + Pelican)
  - [ ] Implement deploy command (orchestrate CDN upload)
- [ ] Set up Pelican configuration
  - [ ] Basic theme selection
  - [ ] Configure output paths
  - [ ] Set up URL structure
- [ ] Create content pages
  - [ ] Gallery index page (/galleries/)
  - [ ] About us page (/about/)
- [ ] Create configuration files
  - [ ] Site orchestration config
  - [ ] NormPic config for wedding collection
  - [ ] Galleria config for wedding gallery

### Phase 3: Integration Testing
- [ ] Test command system end-to-end
- [ ] Validate site generation workflow
- [ ] Test Galleria + Pelican integration

### Phase 4: Performance Baseline
- [ ] Measure initial performance metrics
  - [ ] Page weight (HTML + CSS + thumbnails)
  - [ ] Core Web Vitals (FCP, LCP, TTI, CLS, TBT)
  - [ ] Lighthouse scores
  - [ ] Memory usage during gallery generation and deployment
- [ ] Document baseline metrics
- [ ] Create performance tracking spreadsheet
- [ ] Deployment optimization
  - [ ] Compare CDN manifest with local manifest to determine upload needs
  - [ ] Photo collections: lazy upload (only changed files)
  - [ ] Site content: always upload (smaller transfer, less optimization needed)

## Post-MVP Enhancements

### Near-term Optimizations
- [ ] Comprehensive error handling improvements
  - [ ] Manifest plugin errors (missing files, invalid JSON, version mismatches)
  - [ ] Processor plugin errors (missing photos, corrupted files, permissions)
  - [ ] Template plugin errors (missing themes, invalid syntax, rendering failures)
  - [ ] Pipeline integration errors (plugin loading, dependency conflicts, crashes)
  - [ ] System-level errors (permissions, disk space, memory issues)
- [ ] Dark mode toggle (CSS variables + minimal JS)
- [ ] Gallery performance optimization
  - [ ] Implement lazy loading with JS
  - [ ] Add "Load More" progressive enhancement
  - [ ] Consider intersection observer
  - [ ] Parallel thumbnail processing
  - [ ] Incremental generation (skip unchanged)
  - [ ] Memory-efficient processing for large collections
  - [ ] WebP compression optimization
- [ ] Galleria customization features
  - [ ] Configurable thumbnail sizes
  - [ ] Aspect ratio preservation option
  - [ ] Multiple thumbnail quality settings
  - [ ] Configurable photos per page
- [ ] Galleria theme system
  - [ ] Extract theme to separate module
  - [ ] Create theme base class
  - [ ] Implement theme inheritance
  - [ ] Add dark mode theme variant
- [ ] Add Christmas gallery
- [ ] Add vacation gallery

### Medium-term Features
- [ ] Galleria plugin system implementation
  - [ ] Implement plugin loading mechanism
  - [ ] Create example plugins
    - [ ] EXIF display plugin
    - [ ] Photo download options plugin
    - [ ] Social sharing plugin
- [ ] Photographer web-optimized mirror set handling
  - [ ] Handle photographer web-optimized versions
  - [ ] Fill gaps with auto-generated versions
  - [ ] Size variant selection UI
- [ ] Multiple photo size options for download
- [ ] Gallery search/filter capabilities
- [ ] Galleria output options
  - [ ] JSON data export for JS frameworks
  - [ ] RSS feed generation
  - [ ] Sitemap generation
  - [ ] Open Graph meta tags
- [ ] Blog/updates section
- [ ] Christmas card pages

### Infrastructure Improvements
- [ ] GitHub Actions CI/CD pipeline
- [ ] Docker containerization consideration
- [ ] Ansible automation evaluation
- [ ] CDN optimization (separate bucket strategies)

### Galleria Extraction Preparation
- [ ] Galleria independence audit
  - [ ] Ensure no parent project dependencies
  - [ ] Verify self-contained module structure
  - [ ] Create standalone pyproject.toml for Galleria
  - [ ] Document Galleria-only installation process
- [ ] Galleria technical debt cleanup
  - [ ] Add comprehensive type hints
  - [ ] Improve error messages and logging
  - [ ] Create development/debug mode
  - [ ] Performance optimization and profiling
- [ ] Evaluate extracting schema definitions to shared package
  - [ ] Assess whether NormPic and Galleria should share schema via tiny common package
  - [ ] Consider maintenance overhead vs DRY benefits vs current code duplication
  - [ ] Plan migration strategy if shared package approach is pursued

### Long-term Considerations
- [ ] Django integration for dynamic features
- [ ] CMS integration (Wagtail evaluation)
- [ ] API endpoints for gallery data
- [ ] Mobile app considerations
- [ ] Galleria advanced features (post-extraction)
  - [ ] Video support
  - [ ] RAW file processing
  - [ ] Cloud storage integration
  - [ ] GUI configuration tool

## Success Criteria

MVP is complete when:
1. \u2705 Wedding gallery is live on Bunny CDN
2. \u2705 Gallery index and about pages are live
3. \u2705 Site works without JavaScript
4. \u2705 Performance metrics are documented
5. \u2705 Build process is repeatable via script

## Notes

- Maintain non-JS functionality as primary requirement
- All enhancements must use progressive enhancement
- Performance metrics before and after each optimization
- Keep Galleria extractable for future open-sourcing
- Design plugin interface from day one - modularity is foundational
- Plugin hooks should be lightweight and clearly defined
- Each component should be pluggable without tight coupling