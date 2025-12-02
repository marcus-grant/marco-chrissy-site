# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 3: Integration Testing & Serve Command

- [x] **Implement site serve proxy (TDD cycle)**
  - [x] Create `test/unit/test_site_serve.py` with unit tests for proxy logic
  - [x] `uv run pytest` (tests should fail - RED)
  - [x] Implement `cli/commands/serve.py` with proxy that routes:
    - [x] `/galleries/*` → Galleria serve (port 8001)
    - [x] `/pics/*` → Static file server for output/pics/
    - [x] Everything else → Pelican --listen (port 8002)
  - [x] `uv run pytest` (tests should pass - GREEN)
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Implement site serve proxy command`

- [x] **Enable site serve E2E tests**
  - [x] Remove `@pytest.mark.skip` decorators from `test/e2e/test_site_serve.py`
  - [x] `uv run pytest` (fix any integration issues until tests pass)
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Tst: Enable and fix site serve E2E tests`

- [x] **Document/Plan findings from manual testing of 'serve'**
  **Manual Testing Results:**
  - ✅ Site command pipeline works: validate → organize → build → serve
  - ✅ Pelican routing works: `/` and `/about/` serve correctly
  - ✅ Static file serving works (tested in E2E but not manually)
  - ❌ Galleria routes fail: 502 errors on `/galleries/*` paths
  
  **Critical Issues Found:**
  - **BLOCKING: Galleria hardcoded manifest path bug** - Prepends "config/" to manifest paths
  - **BLOCKING: Galleria hangs processing 645 photos** - Uses 99.9% CPU, never completes
  - **Enhancement: Missing --no-generate flag** in site serve command
  
  **Additional Issues for Later:**
  - [ ] Pelican generating bad routing and site naming (Is it a weird navbar?)
  - [ ] Ongoing issue with galleria's photo links not going to full sized photos
  - [ ] Need configurable base URL for prod vs serve (<http://127.0.0.1:portnum>)

- [ ] **Fix Galleria manifest path bug (BLOCKING)** *(Research complete, implementation blocked by test complexity)*
  - [x] **Investigate Galleria code** - Issue likely in relative path resolution when config passed as "config/galleria.json"
  - [x] **Identified solution** - Use absolute path for config file to prevent relative path resolution issues
  - [ ] **Implement absolute path fix** - Modify serve.py to use absolute config path with proper test mocking
  - [ ] **Clean up workaround** - Remove config/output/pics/full/ directory and manifest copy
  - [ ] **Test manifest path fix** - Verify Galleria reads from correct output/pics/full/ location
  - [ ] **Run full serve test** - Ensure galleries route works without 502 errors
  - [ ] Commit: `Fix: Remove hardcoded config prefix from Galleria manifest paths`

- [ ] **Add --no-generate flag to site serve command** *(Partially implemented, blocked by test environment)*
  - [x] **Research --no-generate flag** - Confirmed flag exists in galleria serve command
  - [x] **Design implementation** - Add CLI option and pass through to galleria subprocess
  - [ ] **Complete TDD implementation** - Write failing test, implement feature, ensure all tests pass
  - [ ] **Test large photo sets** - Verify serve works quickly with 645+ photos
  - [ ] Commit: `Ft: Add --no-generate flag to site serve for development`

- [ ] **Manual testing guide with real photo set** *(BLOCKED until fixes above)*
  - [x] ~~Guide through testing serve command with real photos~~
  - [x] **COMPLETED**: Identified blocking Galleria manifest and performance issues  
  - [ ] **RESUME AFTER FIXES**: Complete full serve testing with working galleries
  - [ ] Test hot reload, file watching, skip generation modes
  - [ ] Verify full E2E workflow works correctly

- [ ] **Document serve command usage**
  - [ ] Create `doc/commands/serve.md` with usage examples and URL pattern explanations
  - [ ] Update `doc/commands/README.md` to link to serve.md
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Doc: Add serve command usage documentation`

- [ ] **Document serve architecture**
  - [ ] Also, update the testing doc with the 'serve' e2e changes
  - [ ] Create `doc/modules/galleria/serve.md` documenting ServeOrchestrator, server, watcher modules
  - [ ] Update `doc/architecture.md` with serve command integration
  - [ ] Update `doc/workflow.md` with development workflow using serve
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Doc: Document serve command architecture and workflow`

### Phase 4: Template & CSS Architecture Fix (Pre-MVP Critical)

- [ ] **Optimize Galleria photo processing performance** (Post-MVP if --no-generate works)
  - [ ] Investigate why 645 photos cause 99.9% CPU hang in Galleria
  - [ ] Implement batched or streaming photo processing  
  - [ ] Add progress indicators for large photo collections
  - [ ] Consider lazy loading or pagination for massive galleries

- [ ] **Refactor template and CSS plugins to use file-based theme system**
  - [ ] CRITICAL: Current template and CSS plugins hardcode HTML/CSS as Python strings (poor architecture)
  - [ ] Move HTML to Jinja2 template files in galleria/themes/*/templates/ directory
  - [ ] Move CSS to static files in galleria/themes/*/static/ directory  
  - [ ] Refactor BasicTemplatePlugin to load and render actual template files
  - [ ] Refactor BasicCSSPlugin to copy/process static CSS files instead of generating strings
  - [ ] Update theme loading system to work with file-based templates and CSS
  - [ ] Preserve existing theme switching functionality but with proper separation of concerns
  - [ ] This addresses the fundamental violation: mixing Python logic with presentation layer

### Phase 5: Performance Baseline

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

### 6: Verify Content Pages & Output Structure

- [ ] E2E test: Full site generation with proper output structure (`test/e2e/`)
- [ ] Unit tests: Output directory management and CDN coordination (`test/unit/build/`)
- [ ] Create Pelican content structure:
  - [ ] Gallery index page (`/galleries/`) - lists available galleries
  - [ ] About page (`/about/`) - personal content
- [ ] Configure output directory structure:

  ```
  output/
  ├── pics/           # Full photos → Photos CDN bucket
  ├── galleries/      # Gallery pages + thumbs → Site CDN
  │   └── wedding/    # URL: /galleries/wedding/page1
  ├── about/          # Pelican pages → Site CDN
  └── index.html      # Site root → Site CDN
  ```

### Phase 7: Deploy Command & Guided Real-World Deployment

- [ ] Plan rest of this step, needs much more detail
- [ ] Set up dual CDN deployment strategy (photos vs site content)

## Post-MVP Enhancements

### Near-term Optimizations

- [ ] **PRIORITY HIGH: Eliminate stateful operations and hardcoded paths**
  - [ ] **Context**: Test infrastructure revealed hardcoded paths and stateful operations throughout codebase
  - [ ] **Current anti-patterns**:
    - [ ] Scattered hardcoded paths like `"config/schema/normpic.json"` cause testing and deployment issues
    - [ ] `os.chdir()` calls in galleria server create stateful contamination between tests
    - [ ] Working directory dependencies make tests fragile and non-isolated
  - [ ] **Solution**: Centralized path configuration with dependency injection and stateless operations
  - [ ] Create PathConfig class with configurable: config_dir, schema_dir, output_dir, temp_dir, working_dir paths
  - [ ] Refactor galleria server to accept `serve_directory` parameter instead of using `os.chdir()`
  - [ ] Refactor ConfigValidator to use PathConfig instead of hardcoded relative paths  
  - [ ] Update all modules to use dependency-injected paths instead of hardcoded strings
  - [ ] Replace all stateful operations with explicit parameter passing
  - [ ] Benefits: deployment flexibility, Docker support, testing isolation, CDN integration, parallel test execution
  - [ ] Enable different path structures for development vs production vs containerized environments
  - [ ] Document path configuration options and deployment scenarios

- [ ] **Refactor plugin output validation to use structured types and schema validation**
  - [ ] Current file writing validation in CLI is defensive programming against malformed plugin output
  - [ ] Design problem: plugins should not be able to generate invalid data structures
  - [ ] Implement proper schema validation at plugin interface level using Pydantic or similar
  - [ ] Create structured output types (e.g., HTMLFile, CSSFile dataclasses) instead of dictionaries
  - [ ] Remove defensive validation from CLI once plugin interfaces are properly typed
  - [ ] Add compile-time type checking for plugin contracts
  - [ ] Update all existing plugins to use new structured output types
- [ ] **E2E test performance optimization**
  - [ ] Fix 16+ second subprocess startup time in E2E tests (unacceptable)
  - [ ] Replace subprocess calls with direct function calls in E2E tests
  - [ ] Consolidate 4 separate E2E tests into single comprehensive workflow test
  - [ ] Achieve 460x performance improvement: 37s → 0.08s for organize E2E tests
  - [ ] Consider pytest-xdist for parallel test execution
  - [ ] Investigate uv run startup overhead with large dependency trees
- [ ] **Verify galleria idempotency behavior**
  - [ ] Verify galleria already handles idempotent rebuilds correctly
  - [ ] Confirm manifest-based change detection works as expected
  - [ ] Document that galleria handles its own change detection (no reimplementation needed)
  - [ ] Test galleria's lazy rebuild behavior with config/template/plugin changes
- [ ] **Enhanced fake image fixture for EXIF testing**
  - [ ] Extend fake_image_factory to create EXIF timestamped photos
  - [ ] Create 5 test images with interesting chronological order for normpic testing
  - [ ] Test normpic's time ordering behavior without camera timestamp collisions
  - [ ] Verify proper handling of sub-second timestamp variations
  - [ ] Test multiple camera scenarios with different timestamp patterns
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
- [ ] Move pelican stuff into a root 'pelican' directory instead of 'content'

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
- [ ] Add Christmas gallery
- [ ] Add vacation gallery

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
  - [ ] Make sure the "Made with galleria" line is a link to the repo
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

### Serve Command Future Enhancements

- [ ] Smart rebuild feature for serve command (incremental rebuilds vs full rebuilds)
- [ ] Configurable plugin/template paths + file watcher integration  
- [ ] Document serve URL patterns for development vs production CDN routing

## Success Criteria

MVP is complete when:

1. [ ] Wedding gallery is live on Bunny CDN
2. [ ] Gallery index and about pages are live
3. [ ] Site works without JavaScript
4. [ ] Performance metrics are documented
5. [ ] Build process is repeatable via script

## Notes

- Maintain non-JS functionality as primary requirement
- All enhancements must use progressive enhancement
- Performance metrics before and after each optimization
- Keep Galleria extractable for future open-sourcing
- Design plugin interface from day one - modularity is foundational
- Plugin hooks should be lightweight and clearly defined
- Each component should be pluggable without tight coupling
