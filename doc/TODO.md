# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development

#### Core Functionality - Plugin System Development

- [x] **Commit 1a: Test Directories + Base Plugin Interface** (COMPLETED)
  - [x] Create test directory structure (e2e/, integration/, unit/)
  - [x] Create `galleria/plugins/base.py` with abstract base plugin class
  - [x] Create unit tests for BasePlugin ABC
  - [x] **Message:** `Ft: Add base plugin interface and test structure`

- [ ] **Commit 1b: Plugin Context/Result Data Structures**
  - [ ] Add PluginContext and PluginResult dataclasses to base.py
  - [ ] Update unit tests for data structures
  - [ ] **Message:** `Ft: Add plugin context and result data structures`

- [ ] **Commit 1c: Plugin Exceptions**
  - [ ] Create `galleria/plugins/exceptions.py` with exception hierarchy
  - [ ] Add unit tests for plugin exceptions
  - [ ] **Message:** `Ft: Add plugin exception hierarchy`

- [ ] **Commit 1d: Hook System + Documentation**
  - [ ] Create `galleria/manager/` directory and hook system
  - [ ] Create E2E integration test for complete plugin workflow
    - (Provider → Processor → Transform → Template → CSS)
  - [ ] **Docs:** Create `doc/modules/galleria/plugin-system.md`
    - Plugin system architecture overview
  - [ ] **Docs:** Update `doc/modules/galleria/README.md` to link to plugin-system.md
  - [ ] **Message:** `Ft: Add plugin hook system and complete foundation`

- [ ] **Commit 2: Plugin Interface Definitions + Integration Tests**
  - [ ] Create failing integration tests for each plugin type interaction
  - [ ] Create ProviderPlugin interface for photo collection sources
  - [ ] Create ProcessorPlugin interface for thumbnail generation
  - [ ] Create TemplatePlugin interface for HTML generation
  - [ ] Create CSSPlugin interface for stylesheet generation
  - [ ] Create PaginationPlugin interface for multi-page support
  - [ ] **Docs:** Update `doc/modules/galleria/plugin-system.md` with interface contracts
  - [ ] **Docs:** Create `doc/modules/galleria/plugin-interfaces.md`
    - Detailed interface specifications
  - [ ] **Message:**
    - `Ft: Add plugin interfaces for provider, processor, template, CSS, pagination`

- [ ] **Commit 3: NormPicProviderPlugin + Unit Tests (TDD)**
  - [ ] Write failing unit tests for NormPicProviderPlugin behavior
  - [ ] Convert existing serializer to proper NormPicProviderPlugin using TDD
    - (red → green → refactor)
  - [ ] Migrate existing serializer tests to work with plugin interface
  - [ ] **Docs:** Update `doc/provider-architecture.md` reflecting plugin system integration
  - [ ] **Docs:** Update `doc/modules/galleria/serializer.md` to document plugin approach
  - [ ] **Message:** `Ref: Convert serializer to NormPicProviderPlugin`

**Commit 4: ThumbnailProcessorPlugin + Unit Tests (TDD)**

- [ ] Write failing unit tests for ThumbnailProcessorPlugin behavior
- [ ] Convert existing processor to proper ThumbnailProcessorPlugin using TDD (red → green → refactor)
- [ ] Migrate existing processor tests to work with plugin interface
- [ ] **Docs:** Update `doc/modules/galleria/processor.md` to document plugin approach
- [ ] **Message:** `Ref: Convert processor to ThumbnailProcessorPlugin`

**Commit 5: Plugin Registry + Integration Tests**

- [ ] Write integration tests for plugin discovery and orchestration
- [ ] Create plugin registry/factory system
- [ ] Implement plugin loading and orchestration mechanisms
- [ ] Test plugin registration and discovery
- [ ] **Docs:** Update `doc/modules/galleria/plugin-system.md` with registry/orchestration details
- [ ] **Message:** `Ft: Add plugin registry and orchestration system`

**Commit 6: Missing Plugins + Unit Tests (TDD)**

- [ ] Write failing unit tests for TemplatePlugin behavior
- [ ] Write failing unit tests for CSSPlugin behavior
- [ ] Write failing unit tests for PaginationPlugin behavior
- [ ] Implement TemplatePlugin using TDD (red → green → refactor)
- [ ] Implement CSSPlugin using TDD (red → green → refactor)
- [ ] Implement PaginationPlugin using TDD (red → green → refactor)
- [ ] **Docs:** Create `doc/modules/galleria/template-plugins.md` - Template/CSS/Pagination plugin documentation
- [ ] **Docs:** Update `doc/modules/galleria/plugin-system.md` with complete plugin catalog
- [ ] **Message:** `Ft: Add template, CSS, and pagination plugins`

**Commit 7: Complete E2E Workflow**

- [ ] Ensure original E2E integration test passes end-to-end
- [ ] Validate all integration and unit tests passing
- [ ] Test complete plugin pipeline: Provider → Processor → Template → CSS → Pagination
- [ ] **Docs:** Update `doc/architecture.md` with plugin system integration
- [ ] **Docs:** Update `doc/README.md` links if new docs added
- [ ] **Message:** `Ft: Complete plugin system with E2E workflow`

**Testing Methodology:** E2E Integration → Unit TDD → Back to Integration → Full E2E validation

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

- [ ] Create **main**.py entry point
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

