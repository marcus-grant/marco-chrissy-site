# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

For detailed planning guidance, templates, and examples, see: **[`PLANNING.md`](PLANNING.md)**

## MVP Roadmap

### Phase 4: Template & CSS Architecture Fix (Pre-MVP Critical)


#### ✅ Task 1.2: Serve Command Cascade (Branch: fix/serve) - COMPLETED

**Status**: Merged to main via PR #13 on 2025-12-05

**Implementation Summary**:
- Added cascade functionality to serve command to auto-call build when output/ missing
- Following the same cascading pattern as other commands (serve→build→organize→validate)  
- Comprehensive test coverage with both unit and E2E tests
- Complete documentation updates in CHANGELOG.md, serve.md, and pipeline.md

**Key Changes**:
- `cli/commands/serve.py`: Added output directory check and build command invocation
- `test/unit/test_site_serve.py`: Added unit tests for cascade behavior
- `test/e2e/test_site_serve.py`: Added E2E test for full cascade functionality
- Documentation updated across multiple files

#### Task 1.3: Template & CSS Architecture (Branch: ft/theme)

*Problem Statement: Template and CSS plugins contain hardcoded HTML strings and CSS styles instead of loading from external theme files. This violates separation of concerns, makes customization difficult, and prevents coherent styling with the parent Pelican site.*

**Phase 1: Setup & Integration Definition**
- [x] `git checkout -b ft/theme`
- [x] Insert nonsensical placeholder returns:
  - [x] `BasicTemplatePlugin._generate_page_html()` → `return "<div>PLACEHOLDER_HTML</div>"`
  - [x] `BasicCSSPlugin._generate_gallery_css()` → `return "/* PLACEHOLDER_CSS */"`
- [x] Run `uv run pytest` to identify failing tests
- [x] Document all failing test modules with specific failure reasons:
  - `test/e2e/test_site_build.py::TestSiteBuild::test_build_uses_orchestrator_pattern` - Build E2E expects real HTML/CSS output
  - `test/galleria/e2e/test_cli_generate.py` - CLI generate expects real gallery HTML/CSS (2 tests)
  - `test/galleria/e2e/test_serve_e2e.py` - Serve E2E expects real generated content (3 tests)  
  - `test/galleria/unit/plugins/test_template.py::TestBasicTemplatePlugin` - Template plugin unit tests expect real HTML structure (3 tests)
  - `test/galleria/unit/test_cli_e2e.py::TestGalleriaCLIE2E::test_cli_generate_command_with_fake_filesystem` - CLI E2E expects real output
- [x] Review failing tests against current TODO.md plan: **ALL COVERED** - Expected template/CSS plugin tests + E2E pipeline tests
- [x] If gaps found: **NO GAPS** - all failing tests are expected categories
- [x] Commit: `Pln: Update theme system plan based on test discovery`
- [x] Evaluate current fixture landscape for theme system needs: **SUFFICIENT** - temp_filesystem, config_file_factory, file_factory cover theme directory creation
- [x] Create theme-specific fixtures if beneficial: **NOT NEEDED** - existing fixtures adequate for theme file creation  
- [x] Create integration test in `test/e2e/test_theme_integration.py`
- [x] Add `@pytest.mark.skip("Theme system not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add theme system integration test (skipped)`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Theme File Structure & Validation*
- [x] Create stub in `galleria/theme/validator.py` with `ThemeValidator` class
- [x] Write unit test for `ThemeValidator.validate_theme_directory()` that fails
- [x] **Test Discovery**: No existing functionality to comment out (new module)
- [x] Implement minimal theme directory validation
- [x] Refactor for better design (keeping tests green)
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Implement theme directory validation`

*Cycle 2: Jinja2 Template Loading*
- [ ] Create stub in `galleria/theme/loader.py` with `TemplateLoader` class
- [ ] Write unit test for `TemplateLoader.load_template()` that fails
- [ ] **Test Discovery**: Comment out new functionality, run tests, identify porting needs
- [ ] Implement minimal Jinja2 template loading from theme directory
- [ ] Refactor for better design (keeping tests green)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Implement Jinja2 template loading`

*Cycle 3: Template Plugin Refactor*
- [ ] Create/modify stub in `galleria/plugins/template.py`
- [ ] Write unit test for theme-based `BasicTemplatePlugin.generate_html()` that fails
- [ ] **Test Discovery**: Comment out new functionality, run tests, identify porting needs
- [ ] Implement theme file integration in BasicTemplatePlugin
- [ ] Refactor for better design (keeping tests green)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Replace hardcoded HTML with Jinja2 templates`

*Cycle 4: CSS Plugin Refactor*
- [ ] Create/modify stub in `galleria/plugins/css.py`
- [ ] Write unit test for theme-based `BasicCSSPlugin.generate_css()` that fails
- [ ] **Test Discovery**: Comment out new functionality, run tests, identify porting needs
- [ ] Implement theme CSS file reading in BasicCSSPlugin
- [ ] Refactor for better design (keeping tests green)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Replace hardcoded CSS with theme files`

*Cycle 5: Test Migration & Cleanup*
- [ ] Port all failing tests identified throughout cycles to work with theme system
- [ ] **Test Discovery**: Remove placeholder implementations, verify all tests pass with theme system
- [ ] Remove commented-out implementation code and placeholders
- [ ] Refactor for better design (keeping tests green)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Migrate existing tests to theme-based implementation`

**Phase 3: Integration & Documentation**
- [ ] Remove `@pytest.mark.skip` from integration test
- [ ] Verify integration test passes (if not, return to Phase 2)
- [ ] Update relevant documentation in `doc/modules/galleria/`
- [ ] Ensure documentation links are maintained
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Update template documentation for theme system`

**Phase 4: PR Creation**
- [ ] `gh pr create --title "Feat: File-based theme system" --body "Replaces hardcoded templates/CSS with configurable theme files"`

### Phase 5: Performance Baseline

- [ ] Measure initial performance metrics
  - [ ] Pipeline timing: validate, organize (16s), build (6m4s), deploy step durations
  - [ ] Thumbnail generation: time per photo, batch processing efficiency  
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
- [ ] **DESIGN ISSUE: Serve command doesn't cascade to build**
  - Manual testing revealed serve fails when output/ doesn't exist
  - Manual testing confirmed serve doesn't detect content changes and auto-rebuild
  - Expected behavior: serve should auto-call build → organize → validate
  - Current behavior: serve assumes build has already been run
  - This violates the cascading pipeline pattern described in CONTRIBUTE.md
  - Non-breaking issue: workaround is manual `site build` before `site serve`
- [x] **PELICAN INTEGRATION ISSUE: File overwrite conflicts** *(RESOLVED)*
  - **Root cause identified**: Pelican's default blog index and custom page with `slug: index` both try to generate `index.html`
  - **Solution implemented**: Smart detection of conflicting content and conditional INDEX_SAVE_AS configuration
  - **Verification complete**: Both test scenarios pass - with and without conflicting index content
  - Manual testing can now proceed without requiring `rm output/index.html && site build` workaround

## MVP 0.1.0 Release Preparation

**Prerequisites**: All Phase 4-7 tasks must be completed first.

### Final Pre-MVP Bookkeeping Tasks

- [ ] **Changelog Migration Verification**
  - [ ] Verify all entries from 2024-12-04 and older moved to `doc/release/0-1.md`
  - [ ] Confirm only 2025-12-05 and newer remain in main `CHANGELOG.md`
  - [ ] Update `doc/release/README.md` with comprehensive 0.1.0 MVP summary

- [ ] **Documentation Quality Assurance** 
  - [ ] Review all 40 documentation files for accuracy and consistency
  - [ ] Verify all internal links work correctly  
  - [ ] Update outdated information and remove "future" annotations for completed features
  - [ ] Standardize formatting, terminology, and structure across all docs

- [ ] **Dead Code Investigation & Removal**
  - [ ] Investigate and remove old non-plugin based manifest serializer
  - [ ] Remove old thumbnail processor that bypassed plugin interfaces  
  - [ ] Scan for unused configuration files or deprecated settings
  - [ ] Remove commented-out code blocks and duplicate implementations

- [ ] **MVP Success Criteria Verification**
  - [ ] Verify build process is repeatable via script
  - [ ] Confirm site works without JavaScript requirement
  - [ ] Test complete pipeline (validate→organize→build) end-to-end
  - [ ] Validate configuration system completeness
  - [ ] Performance metrics documentation

- [ ] **Version 0.1.0 Release Finalization**
  - [ ] Final ruff/pytest run across entire codebase (target: 0 failures)
  - [ ] Update version numbers in relevant files
  - [ ] Create final commit with version bump and release notes
  - [ ] Tag release v0.1.0

## Post-MVP Enhancements

### Near-term Optimizations

#### Task 4: Galleria Performance (Branch: perf/galleria)

- [ ] `git checkout -b perf/galleria`
- [ ] Create `test/performance/test_large_collections.py` with 645 photo test
- [ ] Add `@pytest.mark.skip("Performance optimization not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add performance test for large photo collections (skipped)`

- [ ] Write unit test for batched photo processing that fails
- [ ] Implement batch processing in photo processor plugins
- [ ] Add progress indicators for large collections
- [ ] Remove `@pytest.mark.skip` from performance test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Perf: Implement batched photo processing for large collections`

- [ ] `gh pr create --title "Perf: Optimize large photo collection processing" --body "Fixes CPU hang with 645+ photos via batched processing"`

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

#### Fixture Refactoring (Branch: test/fixtures)

*Problem Statement: Test fixtures have duplication between mock_pelican_config, mock_site_config, and config_file_factory. This creates maintenance overhead and inconsistent test setup patterns. We need to consolidate these into enhanced, reusable fixtures that support both simple and complex configuration scenarios.*

- [ ] `git checkout -b test/fixtures`
- [ ] Analyze existing test fixtures for mock config duplication
- [ ] Write E2E test for comprehensive config fixture usage that fails
- [ ] Add `@pytest.mark.skip("Fixture refactoring not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for fixture refactoring (skipped)`
- [ ] Write unit test for enhanced config_file_factory that fails
- [ ] Enhance config_file_factory to support mock overrides and complex configs
- [ ] Merge mock_pelican_config and mock_site_config into enhanced factories
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Enhance config_file_factory with mock support`
- [ ] Write unit test for centralized test config management that fails
- [ ] Create test_config_factory fixture for common test scenarios
- [ ] Refactor existing tests to use centralized fixtures
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Centralize test configuration fixtures`
- [ ] `gh pr create --title "Test: Refactor config fixtures for reusability" --body "Centralizes and enhances test fixtures to reduce duplication"`

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
