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

- [x] **Commit 5: Plugin Registry + Integration Tests (TDD)** (COMPLETED)
  - [x] PluginRegistry fully implements plugin discovery and orchestration
  - [x] Integration tests demonstrate complete Provider → Processor pipeline
  - [x] Plugin loading mechanism handles dependencies and configuration
  - [x] Documentation updated to reflect orchestration capabilities
  - [x] Test count progression: 161 → 170-180 tests
  - [x] Foundation ready for Commit 6 (Template/CSS/Transform plugins)
  - [x] **Message:** `Ft: Add plugin registry and orchestration system`

- [x] **Commit 6: Missing Plugins + Unit Tests (TDD)** (COMPLETED)
  - [x] TemplatePlugin, CSSPlugin, and PaginationPlugin fully implemented
  - [x] All unit tests passing for new plugin interfaces (28 tests added)
  - [x] E2E test demonstrates complete 5-stage pipeline
  - [x] Documentation updated with plugin usage examples
  - [x] Foundation ready for Commit 7 (Complete E2E Workflow)
  - [x] **Message:** `Complete Template, CSS, and Pagination plugin implementations`

- [x] **Commit 7: E2E Real Plugin Integration (4 small commits)** (COMPLETED)

- [x] **Commit 7a: `Tst: Add real plugin E2E integration tests`** (~75-100 lines)
  - [x] Create failing E2E test using actual NormPicProvider → ThumbnailProcessor → etc.
  - [x] Test PipelineManager orchestrating real plugins (not mocks)
  - [x] Verify test fails as expected (red phase)

- [x] **Commit 7b: `Fix: Plugin registry integration issues`** (~100-150 lines)
  - [x] Fix plugin loading/registration discovered by E2E failure
  - [x] Make E2E test progress further but still fail

- [x] **Commit 7c: `Fix: Data contract validation between plugins`** (~100-150 lines)
  - [x] Fix data format mismatches between real plugins
  - [x] Handle any contract issues discovered by E2E test

- [x] **Commit 7d: `Ft: Complete real plugin E2E workflow`** (COMPLETED IN 7c)
  - [x] Final fixes to make E2E test fully pass (completed in 7c)
  - [x] Real plugin pipeline working end-to-end

**Commit 8: CLI Generate Command (5 small commits)**

- [x] **Commit 8a: `Tst: Add CLI generate command E2E tests`** (~75-100 lines)
  - [x] Create failing E2E test for `galleria generate --config config.json`
  - [x] Test argument parsing, config loading, plugin execution
  - [x] Verify test fails (no CLI exists yet)

- [x] **Commit 8b: `Ft: Add CLI entry point and argument parsing`** (~100-150 lines)
  - [x] Implement `galleria/__main__.py`
  - [x] Basic argument parsing with --config, --output, --verbose flags

- [ ] **Commit 8c: `Ft: Add configuration loading system`** (~100-150 lines)
  - [ ] Implement config file loading and validation
  - [ ] Plugin configuration handling

- [ ] **Commit 8d: `Ft: Implement generate command logic`** (~100-150 lines)
  - [ ] Connect CLI to PipelineManager
  - [ ] Progress reporting and error handling

- [ ] **Commit 8e: `Tst: Validate generate command E2E`** (~50-75 lines)
  - [ ] Ensure E2E test passes fully
  - [ ] Add any missing error handling

**Commit 9: Documentation (1 commit)**

- [ ] **Commit 9a: `Doc: Update architecture and CLI documentation`** (~100-150 lines)
  - [ ] Update `doc/architecture.md` with plugin integration
  - [ ] Document CLI usage and configuration format
  - [ ] Update `doc/README.md` links

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
  - [ ] **CRITICAL**: Unify plugin configuration access patterns
    - [ ] Remove dual config pattern support (nested vs direct)
    - [ ] Standardize on single config approach across all plugins
    - [ ] Update all unit tests to use unified config pattern
    - [ ] Remove backward compatibility config detection code
    - [ ] Choose either: nested stage-specific OR flattened direct access
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
