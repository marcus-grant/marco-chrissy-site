# Marco & Chrissy's Website - TODO

## Next Immediate Tasks

### Serve Command Implementation

See detailed implementation plan in [Phase 3: Integration Testing & Serve Command](#phase-3-integration-testing--serve-command)

## MVP Roadmap

### Phase 2: Site Structure

**Architecture:** 4-stage idempotent pipeline with plugin-based Pelican integration

#### 2.2: CLI Command System (Idempotent Cascading)

- [x] E2E test: `uv run site` command discovery and basic functionality (`test/e2e/`)
- [x] Unit tests: Individual command modules (`test/unit/`)
- [x] Implement `uv run site` command with subcommands
  - [x] `site validate` - Pre-flight checks (config file validation implemented)
  - [x] `site organize` - NormPic orchestration (real integration implemented)
  - [x] `site build` - Galleria + Pelican generation (calls organize if needed)
    - [x] E2E test: Complete build pipeline with fake filesystem and images
    - [x] Unit tests: Build command integration (organize cascade, Python modules)
    - [x] Centralize fake image generation into shared fixtures
    - [x] Implement build command with galleria and pelican integration
    - [x] Verify BeautifulSoup validation of generated HTML content
    - [x] Test idempotent behavior (trust galleria's internal change detection)
  - [ ] `site deploy` - Bunny CDN upload (calls build if needed)
- [ ] Each command checks if work already done and skips unnecessary operations

#### 2.3: Production Configuration Files

- [ ] Production config files: Create actual config files for wedding site
  - [ ] `config/site.json` - Production orchestration settings
  - [ ] `config/normpic.json` - Wedding photo organization settings
  - [ ] `config/pelican.json` - Site generation configuration
  - [ ] `config/galleria.json` - Wedding gallery configuration

#### 2.4: Pelican + Galleria Integration (Plugin-Based)

- [ ] E2E test: Complete plugin-based gallery generation workflow (`test/e2e/`)
- [ ] Unit tests: PelicanTemplatePlugin functionality (`test/unit/plugins/`)
- [ ] Create `PelicanTemplatePlugin` extending Galleria's `TemplatePlugin`
  - [ ] Plugin uses shared Jinja2 templates for consistent navigation/styling
  - [ ] Configure Galleria to use `PelicanTemplatePlugin` instead of `BasicTemplatePlugin`
  - [ ] Maintain Galleria extractability - site-specific logic stays in plugin
- [ ] Set up Pelican with coordinated theme system
  - [ ] Shared template files for navigation/layout components
  - [ ] Configure Pelican theme to match Galleria styling

#### 2.5: Content Pages & Output Structure

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

### Phase 3: Integration Testing & Serve Command

- [x] **Add future enhancement tasks to end of TODO.md**
  - [x] Smart rebuild feature for serve command (incremental rebuilds vs full rebuilds)
  - [x] Configurable plugin/template paths + file watcher integration
  - [x] Document serve URL patterns for development vs production CDN routing
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Pln: Add serve command future enhancement tasks`

- [x] **Add watchdog dev dependency**
  - [x] Add `watchdog` to pyproject.toml dev dependencies
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest` 
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Add development server dependencies`

- [ ] **Replace existing serve command with proper architecture**
  - [ ] Remove old serve command implementation from galleria/__main__.py
  - [ ] Remove old serve tests from test/galleria/e2e/test_cli_serve.py
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest` (may have failures - expected)
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Ref: Remove old serve command implementation`

- [x] **Create new Galleria serve E2E tests (skipped)**
  - [x] Create `test/galleria/e2e/test_serve_e2e.py` with tests:
    - [x] `@pytest.mark.skip` test_galleria_serve_cli_integration - Test CLI starts server, serves files, handles shutdown
    - [x] `@pytest.mark.skip` test_serve_file_watching_workflow - Test config/manifest changes trigger rebuilds  
    - [x] `@pytest.mark.skip` test_serve_static_file_serving - Test HTTP requests return correct gallery files
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest` (tests should be skipped)
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Tst: Add new galleria serve E2E tests (skipped)`

- [x] **Create galleria serve module structure**
  - [x] Create `galleria/orchestrator/serve.py` with ServeOrchestrator class stub
  - [x] Create `galleria/server/__init__.py` with static file server stub
  - [x] Create `galleria/util/watcher.py` with file watcher stub
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Create new galleria serve module structure`

- [x] **Implement file watcher (TDD cycle)**
  - [x] Create `test/galleria/unit/test_watcher.py` with unit tests for file watching
  - [x] `uv run pytest` (tests should fail - RED)
  - [x] Implement `galleria/util/watcher.py` using watchdog library
  - [x] Hard-code paths for galleria config, manifest, template, plugin directories
  - [x] `uv run pytest` (tests should pass - GREEN)
  - [x] Refactor if needed while keeping tests green
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Implement file watcher for galleria serve`

- [x] **Implement static file server (TDD cycle)**
  - [x] Create `test/galleria/unit/test_server.py` with unit tests for HTTP server
  - [x] `uv run pytest` (tests should fail - RED)
  - [x] Implement `galleria/server/__init__.py` using Python's SimpleHTTPRequestHandler
  - [x] `uv run pytest` (tests should pass - GREEN)
  - [x] Refactor if needed while keeping tests green
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Implement static file server for galleria`

- [x] **Implement ServeOrchestrator (TDD cycle)**
  - [x] Create `test/galleria/unit/test_serve_orchestrator.py` with unit tests
  - [x] `uv run pytest` (tests should fail - RED)
  - [x] Implement `galleria/orchestrator/serve.py` to coordinate server + watcher + rebuilds
  - [x] `uv run pytest` (tests should pass - GREEN)
  - [x] Refactor if needed while keeping tests green
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Implement ServeOrchestrator for galleria`

- [x] **Add new galleria serve CLI command (TDD cycle)**
  - [x] Create `test/galleria/unit/test_cli_serve.py` with CLI integration tests
  - [x] `uv run pytest` (tests should fail - RED)
  - [x] Add new serve command to galleria CLI using Click, calls ServeOrchestrator
  - [x] `uv run pytest` (tests should pass - GREEN)
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Ft: Add new galleria serve CLI command`

- [x] **Enable new galleria serve E2E tests**
  - [x] Remove `@pytest.mark.skip` decorators from `test/galleria/e2e/test_serve_e2e.py`
  - [x] `uv run pytest` (fix any integration issues until tests pass)
  - [x] `uv run ruff check --fix --unsafe-fixes`
  - [x] `uv run pytest`
  - [x] Update doc/CHANGELOG.md and doc/TODO.md
  - [x] Commit: `Tst: Enable and fix new galleria serve E2E tests`

- [x] **MAJOR PROGRESS: Fixed broken test infrastructure (14/29 tests fixed)**
  - [x] ✅ **FIXED**: ServeOrchestrator dependency injection - removed file I/O bypassing mocks
  - [x] ✅ **FIXED**: CLI timeout test fixture API - corrected galleria_config_factory usage  
  - [x] ✅ **FIXED**: All 13 ServeOrchestrator unit tests now pass with proper mocking
  - [x] ✅ **FIXED**: ConfigManager now supports path parameters for better dependency injection
  - [x] ✅ **COMMITS**: 3 commits fixing fixture API, dependency injection, and test expectations
  - [x] **PROGRESS**: Reduced failing tests from 29 to 15 (48% improvement)

- [x] **BREAKTHROUGH: Systematic elimination of filesystem isolation violations (75% remaining issues resolved)**
  - [x] ✅ **ROOT CAUSE IDENTIFIED**: Tests load real files with hardcoded `Path("config/schema/file.json")`
  - [x] ✅ **PATTERN ESTABLISHED**: Replace filesystem dependencies with inline mock schemas
  - [x] ✅ **PROOF OF CONCEPT**: Fixed 2 normpic schema tests using mock pattern (da44126)
  - [x] ✅ **COMPLETED**: Applied pattern to remaining 5 schema tests - site, pelican (2), galleria (2) using mock schemas
  - [x] ✅ **COMPLETED**: Fixed config validator filesystem dependencies - eliminated `os.chdir()` anti-pattern
  - [x] ✅ **COMPLETED**: Added `base_path` parameter to ConfigValidator for dependency injection
  - [x] ✅ **COMPLETED**: Fixed serve E2E filesystem contamination - eliminated direct `glob()` usage
  - [x] ✅ **COMPLETED**: Replaced real schema file copying with inline mock schemas
  - [x] ✅ **MAJOR PROGRESS**: Reduced failing tests from 8 to 2 (75% improvement)
  - [ ] **REMAINING**: 2 tests still failing - 1 subprocess startup issue, 1 contamination source
  - [x] ✅ **CRITICAL INSIGHT**: Systematic application of isolation principles vs treating each failure individually

- [ ] **Manual testing guide with real photo set**
  - [ ] Guide through testing serve command with real photos
  - [ ] Test hot reload, file watching, skip generation modes
  - [ ] Verify full E2E workflow works correctly
  - [ ] Document any issues found and solutions

- [ ] **Cleanup test galleries and artifacts**
  - [ ] Remove `test_config/` and `test_output/` directories
  - [ ] Ensure `.gitignore` covers all output directories
  - [ ] Clean up any other test artifacts
  - [ ] Commit: `Ref: Clean up test galleries and artifacts`

- [ ] **Create site serve E2E tests (skipped)**
  - [ ] Create `test/e2e/test_site_serve.py` with tests:
    - [ ] `@pytest.mark.skip` test_site_serve_proxy_coordination - Test site serve starts both Galleria and Pelican servers
    - [ ] `@pytest.mark.skip` test_site_serve_routing - Test proxy routes /galleries/, /pics/, other requests correctly
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Tst: Add site serve E2E tests (skipped)`

- [ ] **Implement site serve proxy (TDD cycle)**
  - [ ] Create `test/unit/test_site_serve.py` with unit tests for proxy logic
  - [ ] `uv run pytest` (tests should fail - RED)
  - [ ] Implement `cli/commands/serve.py` with proxy that routes:
    - [ ] `/galleries/*` → Galleria serve (port 8001)
    - [ ] `/pics/*` → Static file server for output/pics/
    - [ ] Everything else → Pelican --listen (port 8002)
  - [ ] `uv run pytest` (tests should pass - GREEN)
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Ft: Implement site serve proxy command`

- [ ] **Enable site serve E2E tests**
  - [ ] Remove `@pytest.mark.skip` decorators from `test/e2e/test_site_serve.py`
  - [ ] `uv run pytest` (fix any integration issues until tests pass)
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Tst: Enable and fix site serve E2E tests`

- [ ] **Document serve command usage**
  - [ ] Create `doc/commands/serve.md` with usage examples and URL pattern explanations
  - [ ] Update `doc/commands/README.md` to link to serve.md
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Doc: Add serve command usage documentation`

- [ ] **Document serve architecture**
  - [ ] Create `doc/modules/galleria/serve.md` documenting ServeOrchestrator, server, watcher modules
  - [ ] Update `doc/architecture.md` with serve command integration
  - [ ] Update `doc/workflow.md` with development workflow using serve
  - [ ] `uv run ruff check --fix --unsafe-fixes`
  - [ ] `uv run pytest`
  - [ ] Update doc/CHANGELOG.md and doc/TODO.md
  - [ ] Commit: `Doc: Document serve command architecture and workflow`

- [ ] Test command system end-to-end
  - [ ] First check what's already there
- [ ] Validate site generation workflow
- [ ] Test Galleria + Pelican integration

### Phase 4: Template & CSS Architecture Fix (Pre-MVP Critical)

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

### Phase 6: Deploy Command & Guided Real-World Deployment

- [ ] Plan rest of this step, needs much more detail
- [ ] Set up dual CDN deployment strategy (photos vs site content)

## Post-MVP Enhancements

### Near-term Optimizations

- [ ] **PRIORITY HIGH: Refactor hardcoded paths to configuration-based path management**
  - [ ] **Context**: Test infrastructure fixes revealed hardcoded paths throughout codebase (ConfigValidator, schema tests, etc.)
  - [ ] **Current anti-pattern**: Scattered hardcoded paths like `"config/schema/normpic.json"` cause testing and deployment issues
  - [ ] **Solution**: Centralized path configuration in config/site.json with dependency injection
  - [ ] Create PathConfig class with configurable: config_dir, schema_dir, output_dir, temp_dir paths
  - [ ] Refactor ConfigValidator to use PathConfig instead of hardcoded relative paths  
  - [ ] Update all modules to use dependency-injected paths instead of hardcoded strings
  - [ ] Benefits: deployment flexibility, Docker support, testing isolation, CDN integration
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
