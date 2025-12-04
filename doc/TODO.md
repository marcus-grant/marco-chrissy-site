# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

For detailed planning guidance, templates, and examples, see: **[`PLANNING.md`](PLANNING.md)**

## MVP Roadmap

### Phase 4: Template & CSS Architecture Fix (Pre-MVP Critical)


#### Task 1.1: Serve Command Architecture Refactor (Branch: ref/serve)

*Problem Statement: The serve command in `cli/commands/serve.py` has too much logic mixed together, making unit tests increasingly difficult to mock properly. We need to extract business logic to separate modules so unit tests can focus on smaller, testable components while keeping E2E tests as true end-to-end validation.*

**Phase 1: Setup & Test Discovery**
- [ ] `git checkout -b ref/serve` (or merge main if branch exists)
- [ ] Comment out non-CLI logic in `cli/commands/serve.py` (proxy, orchestration, server management)
- [ ] Leave only CLI arg parsing, calling placeholder orchestrator, result reporting
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest` - **expect failures**
- [ ] Review test failures and mark with skip decorators:
  - [ ] Mark failing unit tests with `@pytest.mark.skip("Will migrate to appropriate test modules after logic extraction")`
  - [ ] Mark failing E2E tests with `@pytest.mark.skip("Will work after serve refactor implementation")`
- [ ] Add new E2E test case to verify refactored architecture will work end-to-end
- [ ] Mark new test case with `@pytest.mark.skip("Serve refactor not implemented")`
- [ ] Commit: `Tst: Comment out serve logic and mark tests for migration`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Create Serve Module Structure*
- [x] Create stub `serve/__init__.py`
- [x] Create stub `serve/orchestrator.py` with `ServeOrchestrator` class
- [x] Identify unit tests from Phase 1 that specify orchestrator behavior
- [x] Port those specific tests to `test/unit/test_serve_orchestrator.py`
- [x] Remove skip decorators from ported tests in new location
- [x] Run `uv run pytest test/unit/test_serve_orchestrator.py` - should fail as expected
- [x] Port relevant commented-out logic from serve command to orchestrator
- [x] Run tests again - may still fail, refactor test if needed
- [x] Fix implementation until tests pass
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add ServeOrchestrator class structure`

*Cycle 2: Extract Proxy Logic*
- [x] Create `serve/proxy.py` stub
- [x] Identify unit tests that specify proxy behavior (SiteServeProxy, ProxyHTTPHandler)
- [x] Port those specific tests to `test/unit/test_serve_proxy.py`
- [x] Remove skip decorators, run tests - should fail
- [x] Port proxy classes from commented serve command code (**may not work as-is**)
- [x] If ported code doesn't work: refactor → red → green cycle until tests pass
- [x] Update orchestrator to use extracted proxy
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ref: Extract proxy logic to separate module`

*Cycle 3: Update CLI Command*
- [x] Identify remaining unit tests that specify pure CLI interface behavior
- [x] Keep those tests in original location but update to test new interface
- [x] Remove skip decorators, run tests - should fail
- [x] Refactor `cli/commands/serve.py` to only handle:
  - [x] Argument parsing
  - [x] Calling ServeOrchestrator
  - [x] Result reporting
- [x] Fix CLI tests until they pass with new simplified interface
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ref: Simplify serve command to CLI-only concerns`

**Phase 2.5: CRITICAL BUG INVESTIGATION (serve command hangs indefinitely)** *(COMPLETED)*
- [x] Debug why `uv run site serve` hangs indefinitely during execution
- [x] Analyze `server.serve_forever()` behavior in ServeOrchestrator.start()
- [x] Test minimal serve command execution to isolate root cause of hang
- [x] Investigate server lifecycle and cleanup mechanisms
- [x] Check if subprocess management (Galleria/Pelican) causes blocking
- [x] Fix server hang issue that prevents serve command from working
- [x] Verify serve command executes and terminates properly
- [x] Update E2E tests to work with fixed serve implementation

**SOLUTION IMPLEMENTED:**
- Refactored ServeOrchestrator to avoid deadlocks when shutting down HTTP server
- HTTPServer.serve_forever() runs in background thread via _run_http_server
- Uses _stop_event set by _signal_handler (for SIGINT/SIGTERM)
- Cleanup (proxy + server shutdown) happens in finally block of start(), not from signal handler
- Fixed test_serve_orchestrator_graceful_shutdown_on_signal and kept test_refactored_serve_architecture passing

- [x] Fix unit tests in test/unit/test_serve_orchestrator.py that assume old signal handler behavior:
  - [x] test_signal_handler_calls_cleanup_and_exits → test_signal_handler_sets_stop_event: Assert _stop_event.is_set(), not direct cleanup/sys.exit
  - [x] test_signal_handler_calls_cleanup_directly → test_signal_handler_does_not_call_cleanup_directly: Verify signal handler doesn't call cleanup directly  
  - [x] test_start_runs_server_in_separate_thread_for_signal_handling: Expect target=_run_http_server, not mock_server.serve_forever
- [x] Remove duplicate test methods that were causing F811 ruff errors
- [x] `uv run pytest test/unit/test_serve_orchestrator.py --timeout=5` passes (11/11 tests)
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest --timeout=5` passes (397/425 tests, 27 skipped, 1 timeout unrelated)
- [x] Commit: `Fix: Resolve serve command hanging issue`

**Phase 3: Integration & Documentation**
- [x] Remove `@pytest.mark.skip` from E2E tests marked in Phase 1
- [x] Verify E2E tests pass (if not, return to Phase 2 cycles)
- [x] Remove `@pytest.mark.skip` from new E2E test case
- [x] Verify no remaining skip decorators are related to this refactor
- [x] Update `doc/modules/serve/README.md` with new architecture
- [x] Update `doc/commands/serve.md` with simplified interface
- [x] Update `doc/architecture.md` with separation of concerns explanation
- [x] Remove legacy test classes from test/unit/test_site_serve.py
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Doc: Update serve architecture documentation`

**Phase 4: PR Creation**
- [x] `gh pr create --title "Ref: Extract serve command business logic" --body "Separates CLI concerns from serve orchestration logic for better testability and maintainability"`

**Phase 4.5: Validate Command Skip Decorator Cleanup**
- [ ] Remove `@pytest.mark.skip` from test/e2e/test_site_validate.py validate tests
- [ ] Implement test_validate_checks_dependencies functionality 
- [ ] Implement test_validate_checks_output_permissions functionality
- [ ] Implement test_validate_fails_on_missing_requirements functionality
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Implement remaining validate command functionality`

#### Task 1.2: Serve Command Cascade (Branch: fix/serve)

- [ ] `git checkout -b fix/serve`
- [ ] Modify `test/e2e/test_site_serve.py` - add test case for serve with missing output/ directory
- [ ] Add `@pytest.mark.skip("Cascade not implemented")` to new test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for serve cascade behavior (skipped)`

- [ ] Write unit test for serve output directory checking that fails
- [ ] Implement output directory check in `cli/commands/serve.py`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add output directory existence check to serve`

- [ ] Write unit test for serve auto-calling build command that fails
- [ ] Implement build command invocation when output/ missing
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Serve auto-calls build when output missing`

- [ ] `gh pr create --title "Fix: Serve command cascade to build" --body "Auto-calls build pipeline when output directory missing"`

#### Task 1.3: Template & CSS Architecture (Branch: ft/theme)

- [ ] `git checkout -b ft/theme`
- [ ] Create `test/e2e/test_theme_system.py` with file-based theme loading test
- [ ] Add `@pytest.mark.skip("Theme system not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for file-based theme system (skipped)`

- [ ] Create `themes/basic/theme.json` with theme metadata schema
- [ ] Create `themes/basic/templates/gallery.html.j2` - move HTML from template.py
- [ ] Create `themes/basic/templates/empty.html.j2` - move empty gallery HTML
- [ ] Create `themes/basic/static/css/gallery.css` - move CSS from css.py
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Create basic theme with file-based templates and CSS`

- [ ] Write unit test for theme validation that fails
- [ ] Create `galleria/theme/validator.py` with theme.json schema validation
- [ ] Implement theme directory and file existence checks
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add theme validation system`

- [ ] Write unit test for template plugin refactor that fails
- [ ] Modify `BasicTemplatePlugin` to load Jinja2 templates from theme directory
- [ ] Remove hardcoded HTML strings from template.py
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: Template plugin uses file-based Jinja2 templates`

- [ ] Write unit test for CSS plugin refactor that fails
- [ ] Modify `BasicCSSPlugin` to copy static files from theme directory
- [ ] Remove hardcoded CSS strings from css.py
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ref: CSS plugin copies files from theme directory`

- [ ] `gh pr create --title "Feat: File-based theme system" --body "Replaces hardcoded templates/CSS with configurable theme files"`

#### Task 1.4: Galleria Performance (Branch: perf/galleria)

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
