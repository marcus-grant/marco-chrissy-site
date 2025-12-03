# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Anyone reading this file should be able to
naturally follow our workflow defined in [CONTRIBUTE.md](CONTRIBUTE.md).
Simply following the checklist items below should lead to
following the rules, defined within that document.
The below example, shows formatting and explanations for each task item.

>**NOTE:** The completed top level task is following our workflow correctly.

### Example Top Level Task or Phase

#### Top Level Task Name

- [ ] `git checkout -b commit-prefix/branch-name`
  - Top level tasks should define a new branch with appropriate commit prefix
  - This keeps PRs organized and easy to review
  - It's OK to reuse old branches, they just need to be merged with main 1st
- [ ] Modify or create e2e or integration test module `test/e2e/module_name.py`
  - Task should mention module name
    - Module name should contain main module being tested
  - The idea is for a top-level test to test larger portions of code
    - This usually surfaces missing or broken functionality
    - Leading naturally to more specific specs defined by unit tests
  - Before marking this task complete, check it fails expectantly
- [ ] Add `@pytest.mark.skip("Reason for skipping")` to new test
  - Only high-quality code should be committed
  - A skip tag means you can still commit incomplete work
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
  - Run code formatter and linter
  - Ensure code quality & changes just skip and don't ruin other tests
- [ ] Update TODO.md and CHANGELOG.md
  - Ensure you're logging work
- [ ] `git commit -am "Tst: title of e2e/integration test (skipped)"`
  - Commit with appropriate prefix (probably Tst for tests)
  - Mention module being tested and that it's skipped

- [ ] Create or modify `module/path/filename.py` with `syntaxed-functionality`
  - Specify file path & if needed functionality being added
  - This is meant to be a stub that that can be imported by unit tests
  - **DO NOT** implement functionality yet
- [ ] Write or modify unit test `TestClassName` for each function being tested
  - Specify test class to make or modify
  - Optionally specify the method strings needed in nested tasks
- [ ] Create or modify `ImplementationClassOrFunction` to pass test(s)
  - Optionally include nested sub-tasks for complex implementations
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] `git commit -am "Ft or Fix: title of functionality being added"`
  - This commit is likely a `Ft` or `Fix` type

- Repeat either the above top-level task
  - Depending on if commit can reasonably contain enough cycles
    - You **DO NOT** want massive commits that are hard to review
    - A good rule of thumb is roughly 300 lines of code or less
  - You stop repeating when it's likely you can remove the skip decorator
  - Do try and add enough unit tests to have decent edge-case coverage
  - Not end of world if you missed something
  - This process makes it easy to make fixes later

- [ ] Remove `@pytest.mark.skip` from test of `test/e2e/module_name.py`
  - The intention is to run the test and verify it passes
    - If not, leave the skip, add tasks above for unit tests to fix it
    - Leave this task uncompleted until test passes

- Here you repeat expected e2e or integration test spec tasks
  - Should have the same sequence as above
  - If you have roughly a dozen or so...
    - Your plan probably needs rethinking or breaking into smaller pieces
    - PRs should be smaller than that for easier review

- [ ] Add or update `doc/subtopic/article.md`
  - There is likely going to be at least one of these tasks per PR
  - Remember the `README.md` adjacency links
    - Each sub-directory of `doc/` has a `README.md`
    - Each `README.md` acts as a overview and index for that topic
    - Each `README.md` links to:
      - Another markdown document in that directory, or...
      - A `README.md` in a sub-directory, representing a sub-topic
      - This forms an adjacency list structure for documentation navigation
      - Don't link to a non-README file in a sub-directory
        - This keeps navigation consistent and predictable
    - Each time you add a document or sub-topic...
      - Update the parent directory's `README.md` to link to it
      - If you create a sub-directory...
        - update the parent `README.md` to link to its `README.md`

## MVP Roadmap

### Phase 4: Template & CSS Architecture Fix (Pre-MVP Critical)

#### Task 1: Configurable Base URLs (Branch: fix/url)

- [x] `git checkout -b fix/url`
- [x] Modify `test/e2e/test_site_serve.py` - add test case that verifies serve command generates localhost URLs in HTML output
- [x] Add `@pytest.mark.skip("URL override not implemented")` to new test
- [x] `uv run ruff check --fix --unsafe-fixes`
- [x] `uv run pytest` (test should be skipped)
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Add E2E test for serve URL override (skipped)`

- [x] Create `build/context.py` with `BuildContext` class having `production: bool` property
- [x] Write unit test for BuildContext that fails
- [x] Implement BuildContext class to pass test
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md  
- [x] Commit: `Ft: Add BuildContext with production flag`

- [x] Modify `PelicanBuilder.build()` to accept `override_site_url` parameter
- [x] Write unit test that fails for URL override functionality
- [x] Implement URL override logic: `'SITEURL': override_site_url or pelican_config.get('site_url', '')`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add site URL override to PelicanBuilder`

- [x] Create template filters in new `galleria/template/filters.py`
- [x] Write unit test for `full_url` filter that fails
- [x] Implement Jinja2 filter that uses BuildContext for URL generation
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add template URL filters for context awareness`

- [x] **TDD VIOLATION HALT**: Session stopped due to implementing template plugin integration without tests first
- [x] **RESTART REQUIRED**: Must write unit tests for template plugin BuildContext integration before implementation

- [x] Write unit test for BasicTemplatePlugin accepting BuildContext via metadata that fails
- [x] Write unit test for BasicTemplatePlugin using full_url filter with context that fails
- [x] Implement BasicTemplatePlugin metadata context access to pass tests
- [x] Modify `galleria/plugins/template.py` to use filters instead of `_make_relative_path()`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Template plugin uses context-aware URL filters`

- [x] Write unit test for GalleriaBuilder accepting BuildContext parameters that fails
- [x] Write unit test for GalleriaBuilder passing BuildContext in metadata that fails
- [x] Implement GalleriaBuilder.build() BuildContext parameter support
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: GalleriaBuilder accepts BuildContext for URL generation`

- [x] Write unit test for BuildOrchestrator passing BuildContext to GalleriaBuilder that fails
- [x] Write unit test for BuildOrchestrator creating BuildContext from override_site_url that fails
- [x] Implement BuildOrchestrator BuildContext integration
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: BuildOrchestrator coordinates context-aware builds`

- [ ] Update `doc/architecture.md` - Add BuildContext system section
  - [ ] Document BuildContext class purpose and production vs development modes
  - [ ] Explain context-aware URL generation architecture  
  - [ ] Update system overview with new build flow
- [ ] Update `doc/modules/build/README.md` - Document GalleriaBuilder BuildContext support
  - [ ] Add BuildContext parameter documentation to GalleriaBuilder.build()
  - [ ] Document metadata passing to galleria pipeline
- [ ] Update `doc/modules/galleria/README.md` - Document template filters module
  - [ ] Add `galleria/template/filters.py` module documentation  
  - [ ] Document full_url filter API and BuildContext integration
- [ ] Update `doc/provider-architecture.md` - Document plugin metadata flow
  - [ ] Add BuildContext metadata passing patterns
  - [ ] Document how plugins access build context via PluginContext.metadata
- [ ] Update serve command documentation - Document URL override capability
  - [ ] Update serve workflow with BuildContext usage patterns
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Doc: Update documentation for BuildContext system`

- [ ] `gh pr create --title "Fix: Configurable base URLs for serve vs build" --body "Implements URL override system for development vs production"`

#### Task 1.1: Serve Command Architecture Refactor (Branch: ref/serve)

*Note: This task needs proper TDD planning. Consider commenting out code first to see which tests fail, revealing what needs to move to new modules.*

- [ ] `git checkout -b ref/serve`
- [ ] Extract business logic from `cli/commands/serve.py`
- [ ] Move `SiteServeProxy`, `ProxyHTTPHandler`, build orchestration to separate module
- [ ] Leave only CLI arg parsing, calling serve manager, result reporting in command
- [ ] Fix test isolation issues caused by build integration in command module
- [ ] Update/move tests that break when logic moves to new modules
- [ ] Write unit test that fails for serve URL passing to extracted orchestrator
- [ ] Implement serve command URL override: pass `http://127.0.0.1:8000` to build via extracted orchestrator
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] `gh pr create --title "Refactor: Extract serve command business logic" --body "Separates CLI concerns from serve orchestration logic"`

*Problem: Serve command currently violates separation of concerns by mixing CLI handling with HTTP proxy logic, build orchestration, and server management. This causes test isolation issues and makes the command difficult to test properly.*

#### Task 1.2: Fixture Refactoring (Branch: test/fixtures)

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

#### Task 2: Serve Command Cascade (Branch: fix/serve)

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

#### Task 3: Template & CSS Architecture (Branch: ft/theme)

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
