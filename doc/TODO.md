# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

For detailed planning guidance, templates, and examples, see: **[`PLANNING.md`](PLANNING.md)**

## MVP Roadmap

### Phase 5: Site Navigation & Layout Integration

#### Task 5.1: Fix Shared Component Integration (Branch: fix/shared-components)

*Problem Statement: Shared component infrastructure exists but build systems don't use it, resulting in missing navigation and inconsistent styling between Pelican and Galleria pages.*

**❌ INTEGRATION FAILURES - Infrastructure Built But Not Connected**

Root Cause: Shared component infrastructure exists and tests pass, but build systems were never configured to use the shared components.

Critical Issues:
- [ ] **Build Integration**: Galleria and Pelican builds don't use shared theme system
- [ ] **Missing Navigation**: Neither system renders navigation components 
- [ ] **Gallery URL Routing**: Links point to `/galleries/` (empty) not `/galleries/wedding/` (actual gallery)
- [ ] **Config Processing**: `galleria/config.py` doesn't handle `theme.external_templates` properly

**Must Fix**: E2E tests pass but don't verify actual build integration - tests are insufficient.

**Phase 1: Setup & E2E Definition**

- [ ] `git checkout -b fix/shared-components`
- [ ] Fix E2E test in `test/e2e/test_shared_components.py`
  - [ ] Test navigation appears in generated HTML files (not just infrastructure)
  - [ ] Test PicoCSS is included in final page HTML
  - [ ] Test shared templates are rendered in build output
  - [ ] Verify both Pelican and Galleria builds use shared components
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Fix E2E tests to verify build integration`

**Phase 2: Integration Discovery & Planning**

- [ ] **PAUSE FOR ANALYSIS**: Run improved E2E tests to identify integration gaps
- [ ] Analyze E2E test failures to map missing integration points
- [ ] Design external theme specification for future Galleria extraction
  - [ ] Config format that works when Galleria is imported package
  - [ ] External template/asset specification patterns
- [ ] **PAUSE FOR PLANNING**: Plan specific unit tests needed based on findings
- [ ] Update TODO.md with detailed TDD cycles for discovered gaps
- [ ] Commit: `Pln: Document integration gaps and unit test plan`

**Phase 3: TDD Implementation Cycles**

*Cycle 1: Create defaults.py Module*

- [ ] Write unit test for `defaults.get_output_dir()` that fails
- [ ] Create `defaults.py` with `get_output_dir()` function  
- [ ] Implement function to return Path("output")
- [ ] Test function returns Path object, not string
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add defaults module for path configuration`

*Cycle 2: Fix Serve Command Hardcoded Path*

- [ ] Write unit test for serve command using `get_output_dir()` that fails
- [ ] Update `cli/commands/serve.py` to import and use `defaults.get_output_dir()`
- [ ] Replace `if not os.path.exists("output"):` with `if not get_output_dir().exists():`
- [ ] Replace second `os.path.exists("output")` with same pattern
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Fix: Replace hardcoded output path with defaults module`

*Cycle 3: Remove Skip Decorators and Fix Serve Tests*

- [ ] Write unit test that mocks `defaults.get_output_dir()` and verifies serve works
- [ ] Remove `@pytest.mark.skip` decorators from serve command tests
- [ ] Update test imports to include `@patch('cli.commands.serve.get_output_dir')`
- [ ] Fix test mocking to use temp directories instead of hardcoded "output"
- [ ] Verify all 6 previously skipped serve tests now pass
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Enable serve command tests with defaults mocking`

*Cycle 4: Add Shared Component Path Defaults*

- [ ] Write unit test for shared component path getters that fails
- [ ] Add `get_shared_template_paths()` and `get_shared_css_paths()` to defaults.py
- [ ] Update `themes/shared/utils/template_loader.py` to use defaults
- [ ] Update `themes/shared/utils/asset_manager.py` to use defaults
- [ ] Test that functions return lists of Path objects for external compatibility
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add shared component path defaults for external usage`

*Cycle 5: Add True Shared Component Integration Tests*

- [ ] Write E2E test that verifies shared components appear in both Pelican and Galleria HTML output
- [ ] Create mock shared navbar template: `<nav class="shared-nav">Test Navbar</nav>`
- [ ] Create mock shared CSS file: `.shared-nav { color: blue; background: red; }`
- [ ] Test that `uv run site build` includes shared navbar HTML in both system outputs
- [ ] Test that shared CSS file is copied to output and referenced in both HTML outputs
- [ ] Assert "Test Navbar" text appears in generated Pelican pages
- [ ] Assert "Test Navbar" text appears in generated Galleria pages
- [ ] Assert CSS rule `.shared-nav { color: blue; background: red; }` exists in output
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E tests for true shared component integration`

*Cycle 6: Remove All Skip Decorators and Verify Complete Integration*

- [ ] Remove `@pytest.mark.skip` from real plugin integration test in `test_real_plugin_integration.py`
- [ ] Update real plugin test to expect 3 files (including index.html redirect)
- [ ] Remove any remaining skip decorators from serve command tests (if not done in Cycle 3)
- [ ] Run full test suite and verify all 452 tests pass with 0 skipped
- [ ] If any tests fail, add unit tests to fix the underlying integration issues
- [ ] Verify shared navbar appears in both Pelican and Galleria build outputs
- [ ] Verify shared CSS is included in both system outputs
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Remove all skip decorators and verify complete integration`

**Phase 4: Production URL Fix**

- [ ] Find all hardcoded `/galleries/` links in templates/code
- [ ] Replace with `/galleries/wedding/` links
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Fix: Update gallery links to point to actual gallery`

**Phase 5: Manual Integration Verification**

- [ ] **Manual Build Test**: Guide user through `uv run site build`
  - [ ] Verify shared navigation appears in output HTML
  - [ ] Check PicoCSS inclusion in generated pages
  - [ ] Confirm `/galleries/wedding/` links work
- [ ] **Manual Serve Test**: Guide user through `uv run site serve`
  - [ ] Test navigation between Pelican and Galleria pages
  - [ ] Verify consistent styling across page types

**Phase 6: Documentation Updates**

- [ ] Update existing documents:
  - [ ] `doc/modules/galleria/themes.md` - External template configuration
  - [ ] `doc/configuration.md` - Shared theme configuration options
  - [ ] `doc/architecture.md` - Shared component integration patterns
- [ ] Create missing documents:
  - [ ] `doc/modules/shared/README.md` - Shared theme system overview
  - [ ] `doc/modules/shared/external-integration.md` - External project compatibility
- [ ] Update navigation in `doc/README.md` to include shared theme docs
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Add shared component integration documentation`

**Phase 7: PR Creation**

- [ ] `gh pr create --title "Fix: Integrate shared components into build systems" --body "Fixes integration failures from previous shared components PR by ensuring build systems actually use shared navigation and CSS components"`

#### Task 5.2: Mobile-First Responsive Layout (Branch: ft/responsive-layout)

*Problem Statement: Site lacks mobile optimization with poor touch targets, non-responsive gallery grid, and inconsistent mobile experience across page types.*

**Phase 1: Setup & E2E Definition**

- [ ] `git checkout -b ft/responsive-layout`
- [ ] Create E2E test in `test/e2e/test_responsive_layout.py`
  - [ ] Test layout works correctly at mobile viewports (320px, 480px, 768px)
  - [ ] Verify gallery grid adapts from 1→2→4 columns based on screen size
  - [ ] Test touch targets meet 44px minimum requirement
  - [ ] Verify desktop layout maintains full functionality
  - [ ] Add `@pytest.mark.skip("Responsive layout not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for responsive layout (skipped)`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Implement Mobile-First Gallery Grid*

- [ ] Write unit test for responsive grid CSS generation that fails
- [ ] Create mobile-first CSS Grid system in gallery templates
- [ ] Implement breakpoints: 480px (1→2 cols), 768px (2→3 cols), 1024px (3→4 cols)
- [ ] Test gallery grid adapts correctly at each breakpoint
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Implement mobile-first responsive gallery grid`

*Cycle 2: Create Touch-Friendly Navigation*

- [ ] Write unit test for touch target sizing that fails
- [ ] Update navigation CSS with 44px minimum touch targets
- [ ] Implement touch-friendly pagination controls
- [ ] Add hover and active states for better touch feedback
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add touch-friendly navigation with proper target sizing`

*Cycle 3: Responsive Typography and Spacing*

- [ ] Write unit test for responsive typography that fails
- [ ] Implement fluid typography scaling using CSS clamp()
- [ ] Add responsive spacing and padding for mobile readability
- [ ] Ensure consistent responsive behavior across Pelican and Galleria pages
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add responsive typography and spacing system`

**Phase 3: Integration & Documentation**

- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes (if not, return to Phase 2)
- [ ] Update `doc/testing.md` with responsive testing patterns
- [ ] Create mobile design guidelines in `doc/architecture.md`
- [ ] Document post-MVP JS enhancement plans in `doc/future/`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Add responsive design documentation and testing guidelines`

**Phase 4: PR Creation**

- [ ] `gh pr create --title "Ft: Implement mobile-first responsive layout" --body "Creates responsive design system with touch-friendly navigation, mobile-optimized gallery grid, and consistent mobile experience across all page types"`

### Phase 6: Performance Baseline

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

### Priority Issues

- [ ] **Galleria Performance**: Optimize large photo collection processing (645+ photos cause CPU hang)
- [ ] **Eliminate Hardcoded Paths**: Create PathConfig class for dependency injection, remove `os.chdir()` calls
- [ ] **Plugin Output Validation**: Use structured types (Pydantic) instead of defensive CLI validation
- [ ] **E2E Test Performance**: Fix 16+ second subprocess startup time, consolidate tests

### Performance Optimizations  

- [ ] Gallery lazy loading with JS progressive enhancement
- [ ] Parallel thumbnail processing and incremental generation
- [ ] WebP compression optimization
- [ ] Dark mode toggle (CSS variables + minimal JS)

### Code Quality

- [ ] Comprehensive error handling for plugin failures
- [ ] Verify galleria idempotency behavior and manifest-based change detection
- [ ] Enhanced fake image fixtures for EXIF testing
- [ ] Remove dead code (old manifest serializer, thumbnail processor)

### Medium-term Features

- [ ] **External Asset Version Pinning**: Add version control for reproducible builds (config-based pinning with integrity hashes vs lock files) - update themes/shared/utils/asset_manager.py

#### Test Infrastructure

- [ ] **Fixture Refactoring**: Consolidate mock_pelican_config, mock_site_config, and config_file_factory
- [ ] Refactor large integration/e2e tests in galleria plugin system  
- [ ] Create reusable mock plugin factories for consistent test data

#### Gallery Enhancements

- [ ] Galleria plugin system: EXIF display, photo download options, social sharing
- [ ] Gallery search/filter capabilities
- [ ] Multiple photo size options and photographer web-optimized mirror sets
- [ ] JSON data export, RSS feeds, sitemap generation, Open Graph meta tags

#### Site Content

- [ ] Blog/updates section
- [ ] Christmas and vacation galleries  
- [ ] Christmas card pages

#### Infrastructure

- [ ] GitHub Actions CI/CD pipeline
- [ ] Docker containerization and Ansible automation evaluation
- [ ] CDN optimization with separate bucket strategies

#### Galleria Extraction Preparation  

- [ ] Independence audit (remove parent project dependencies)
- [ ] Technical debt cleanup (type hints, error handling, performance)
- [ ] Evaluate shared schema package with NormPic

#### Long-term Considerations

- [ ] Django/Wagtail integration for dynamic features
- [ ] API endpoints for gallery data
- [ ] Galleria advanced features: video support, RAW processing, cloud storage, GUI tools

## Success Criteria

MVP is complete when:

1. [ ] Wedding gallery is live on Bunny CDN
2. [ ] Gallery index and about pages are live
3. [ ] Site works without JavaScript
4. [ ] Performance metrics are documented
5. [ ] Build process is repeatable via script

## Future Architecture Planning

Post-MVP modularization strategy documented in [Future Architecture](future/). Key goals:

- Extract Galleria as standalone project
- Create SiteForge framework for static+dynamic sites  
- Enable endpoint abstraction (same logic → static/FastAPI/HTMX/edge functions)
- Transform this repo to configuration/deployment hub

## Notes

- Maintain non-JS functionality as primary requirement
- All enhancements must use progressive enhancement
- Performance metrics before and after each optimization
- Keep Galleria extractable for future open-sourcing
- Design plugin interface from day one - modularity is foundational
- Plugin hooks should be lightweight and clearly defined
- Each component should be pluggable without tight coupling
