# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development

#### Core Functionality - Plugin System Development

- [x] **Commit 3: NormPicProviderPlugin + Unit Tests (TDD)** (COMPLETED)
  - [x] Write failing unit tests for NormPicProviderPlugin behavior
  - [x] Convert existing serializer to proper NormPicProviderPlugin using TDD
    - (red → green → refactor)
  - [x] Migrate existing serializer tests to work with plugin interface
  - [x] **Docs:** Update `doc/provider-architecture.md` reflecting plugin system integration
  - [x] **Docs:** Update `doc/modules/galleria/serializer.md` to document plugin approach
  - [x] **Message:** `Ref: Convert serializer to NormPicProviderPlugin`

- [x] **Commit 4: ThumbnailProcessorPlugin + Unit Tests (TDD)** (COMPLETED)
- [x] Write failing unit tests for ThumbnailProcessorPlugin behavior
- [x] Convert existing processor to proper ThumbnailProcessorPlugin using TDD (red → green → refactor)
- [x] Migrate existing processor tests to work with plugin interface
- [x] **Docs:** Update `doc/modules/galleria/processor.md` to document plugin approach
- [x] **Message:** `Ref: Convert processor to ThumbnailProcessorPlugin`

**Commit 5: Plugin Registry + Integration Tests (TDD)**

**Phase 1: E2E Integration Tests (Red Phase)**
- [ ] Create `test/test_plugin_integration.py` with failing E2E tests
- [ ] Write test for complete Provider → Processor pipeline via registry
- [ ] Write test for plugin discovery and registration workflow
- [ ] Write test for orchestrated workflow from NormPic manifest to thumbnails
- [ ] Verify all integration tests FAIL initially (red phase requirement)

**Phase 2: Unit Tests (Red Phase)**
- [ ] Create `test/galleria/test_plugin_registry.py` with failing unit tests
- [ ] Write tests for `PluginRegistry.register()` method behavior
- [ ] Write tests for `PluginRegistry.get_plugin()` method behavior
- [ ] Write tests for plugin discovery mechanisms
- [ ] Write tests for error handling (missing/duplicate plugins)
- [ ] Verify all unit tests FAIL initially (red phase requirement)

**Phase 3: Implementation (Green Phase)**
- [ ] Implement `galleria/plugins/registry.py` - `PluginRegistry` class
  - [ ] Plugin registration and discovery functionality
  - [ ] Plugin loading with error handling
  - [ ] Plugin dependency resolution
- [ ] Implement `galleria/manager/pipeline.py` - `PipelineManager` class
  - [ ] Stage execution coordination
  - [ ] Integration with existing `PluginHookManager`
  - [ ] Data flow management between plugin stages
- [ ] Make failing unit tests pass one by one (green phase)
- [ ] Make failing integration tests pass (green phase)

**Phase 4: Documentation & Validation**
- [ ] **Docs:** Update `doc/modules/galleria/plugin-system.md` section on plugin registry
  - [ ] Add `PluginRegistry` API documentation with examples
  - [ ] Add `PipelineManager` orchestration documentation
  - [ ] Add plugin discovery workflow documentation
- [ ] **Docs:** Add new section to `doc/modules/galleria/plugin-system.md` on orchestration
  - [ ] Document complete pipeline execution patterns
  - [ ] Add configuration examples for plugin loading
  - [ ] Add troubleshooting guide for plugin discovery issues
- [ ] Run full test suite to ensure no regressions
- [ ] Verify test count reaches 170-180 tests target
- [ ] **Message:** `Ft: Add plugin registry and orchestration system`

**Expected Outcomes After Commit 5:**
- PluginRegistry fully implements plugin discovery and orchestration
- Integration tests demonstrate complete Provider → Processor pipeline
- Plugin loading mechanism handles dependencies and configuration
- Documentation updated to reflect orchestration capabilities
- Test count progression: 161 → 170-180 tests
- Foundation ready for Commit 6 (Template/CSS/Transform plugins)

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
- [ ] Investigate dead code or re-implemented code
  - [ ] Old non-plugin based manifest serializer module based on normpic's code
  - [ ] Old thumbnail processor that didn't use the plugin interfaces
  - [ ] Anything else
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
- [ ] Test refactoring for maintainability
  - [ ] Refactor large integration/e2e tests in galleria plugin system
  - [ ] Extract common test fixtures for plugin interface testing
  - [ ] Split unwieldy test methods into focused, composable test functions
  - [ ] Create reusable mock plugin factories for consistent test data
  - [ ] Implement parametrized tests for plugin contract validation
  - [ ] Consider pytest fixtures for pipeline stage setup/teardown
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
