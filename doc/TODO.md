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

**Phase 3: TDD Implementation Cycles**

*Cycle 5: Add True Shared Component Integration Tests*

- [x] Write E2E test that verifies shared components appear in both Pelican and Galleria HTML output
- [x] Create mock shared navbar template: `<nav class="shared-nav">Test Navbar</nav>`
- [x] Create mock shared CSS file: `.shared-nav { color: blue; background: red; }`
- [x] Test that `uv run site build` includes shared navbar HTML in both system outputs
- [x] Test that shared CSS file is copied to output and referenced in both HTML outputs
- [x] Assert "Test Navbar" text appears in generated Pelican pages
- [x] Assert "Test Navbar" text appears in generated Galleria pages
- [x] Assert CSS rule `.shared-nav { color: blue; background: red; }` exists in output
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Add integration test for shared component build verification`

*Cycle 6: Remove All Skip Decorators and Verify Complete Integration*

- [x] Remove `@pytest.mark.skip` from real plugin integration test in `test_real_plugin_integration.py`
- [x] Update real plugin test to expect 3 files (including index.html redirect)
- [x] Remove any remaining skip decorators from serve command tests (if not done in Cycle 3)
- [x] Run full test suite and verify all 455 tests pass with 8 skipped
- [x] If any tests fail, add unit tests to fix the underlying integration issues
- [x] Verify shared navbar appears in both Pelican and Galleria build outputs
- [x] Verify shared CSS is included in both system outputs
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Remove all skip decorators and verify complete integration`

**Phase 4: Production URL Fix**

- [x] Find all hardcoded `/galleries/` links in templates/code
- [x] Replace with `/galleries/wedding/` links
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Fix: Update gallery links to point to actual gallery`

**BLOCKING ISSUE: Shared Component Integration Still Not Working**

❌ **CRITICAL:** The shared component integration that was supposed to be implemented in the previous PR and fixed in this PR still does not work. Manual testing shows shared navbar is missing from gallery pages, and the one real test that matters proves shared components are not appearing in either Pelican or Galleria generated pages.

**Root Cause:** All existing "integration" and "E2E" tests are worthless - they test infrastructure mocking instead of actual HTML output. The real test (`test_shared_navbar_integration.py`) shows:
1. Pelican builds successfully but `{% include 'navbar.html' %}` appears as literal text, not rendered HTML
2. Galleria template system has no shared template support at all
3. Hundreds of lines of existing tests verify nothing useful

**Required Fix Before Any Manual Testing:**

**Phase 5A: Fix Shared Component Integration (BLOCKING)** ✅ **COMPLETED**

*Cycle 1: Definitive Integration Test* ✅ **COMPLETED**

- [x] Created `test_shared_navbar_integration.py` - the definitive test that verifies actual HTML output
- [x] Mock shared CSS file with vibrant ugly color (`background: #ff00ff`)
- [x] Mock shared navbar with clear ID attribute (`<nav id="test-shared-navbar">`)
- [x] Test builds both Pelican and Galleria successfully
- [x] Assert generated HTML contains shared navbar and CSS for BOTH systems

*Cycle 2: Pelican Shared Template Integration* ✅ **COMPLETED**

- [x] Fixed Pelican template include processing (`{% include 'navbar.html' %}`)
- [x] Configured THEME_TEMPLATES_OVERRIDES and JINJA2CONTENT_TEMPLATES
- [x] Ensured shared templates are found and rendered in Pelican build
- [x] Integration test shows Pelican navbar working

*Cycle 3: Pelican CSS Integration* ✅ **COMPLETED**

- [x] Created `theme_factory` pytest fixture for systematic theme testing
- [x] Configured CSS_FILE and THEME settings for automatic shared CSS inclusion
- [x] Auto-include first shared CSS file via THEME_STATIC_PATHS
- [x] Created unit test `test_build_configures_css_file_for_shared_css`
- [x] Integration test shows Pelican CSS linking working

**CRITICAL FIXTURES CREATED:**

- **`theme_factory(theme_name, css_files=dict, templates=dict)`**: Creates complete theme structures with CSS and templates for testing
- **Usage**: `theme_factory("shared", css_files={"shared.css": "..."}, templates={"base.html": "..."})`
- **Location**: `test/unit/build/test_pelican_builder.py:237-286`
- **Status**: Ready for reuse across all theme-related tests

*Cycle 4: Galleria Shared Template Integration* 🔄 **IN PROGRESS**

- [ ] Write unit test for Galleria shared template inclusion that fails
- [ ] Add shared template support to Galleria template generation system
- [ ] Modify gallery page generation to include shared navbar
- [ ] Ensure generated gallery pages include shared components
- [ ] Update TODO.md and CHANGELOG.md

*Cycle 5: Galleria CSS Integration*

- [ ] Write unit test for Galleria CSS copying and linking
- [ ] Implement CSS integration in Galleria build system
- [ ] Verify integration test passes completely

*Cycle 6: Test Cleanup* **NEW REQUIREMENT**

- [ ] **DELETE worthless mock-based integration tests** that don't verify actual HTML output
- [ ] **REFACTOR existing tests** to use `theme_factory` fixture for consistency
- [ ] Keep only tests that verify real functionality (shared components in builder outputs)
- [ ] Reduce test suite execution time by removing wheel-spinning tests
- [ ] Document `theme_factory` usage in test guidelines

**Phase 5A.1: BLOCKING - Pelican Shared Component Configuration** ✅ **COMPLETED**

*Problem: Galleria uses `shared_theme_path` while Pelican uses `THEME_TEMPLATE_OVERRIDES`. This configuration mismatch prevents shared components from working in Pelican, causing different navbars in site index vs gallery pages.*

*Cycle 1: Add E2E Test for Real Output Verification*

- [x] Modified existing `test_shared_navbar_integration.py` instead of creating new test
- [x] Updated test to use `THEME_TEMPLATE_OVERRIDES` for both systems
- [x] Initially marked with `@pytest.mark.skip("Pelican config alignment not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Update E2E test for config alignment`

*Cycle 2: Update Unit Tests for New Configuration*

- [x] Found existing tests that reference `shared_theme_path`
- [x] Updated unit tests in `test/e2e/test_shared_components.py` to use `THEME_TEMPLATE_OVERRIDES`
- [x] Updated galleria plugin tests to expect new config key
- [x] Updated template loader tests to use Pelican-standard naming
- [x] Tests failed as expected because implementation still used old key
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Update unit tests for config alignment`

*Cycle 3: Update Galleria Implementation*

- [x] Updated `build/galleria_builder.py` to read `THEME_TEMPLATE_OVERRIDES` instead of `shared_theme_path`
- [x] Updated `galleria/plugins/template.py` to use new config key
- [x] Updated `config/schema/galleria.json` to replace `shared_theme_path` with `THEME_TEMPLATE_OVERRIDES`
- [x] Unit tests now pass
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ref: Update Galleria config key alignment`

*Cycle 4: Fix Pelican Configuration*

- [x] Updated `config/pelican.json` and `config/galleria.json` to use `THEME_TEMPLATE_OVERRIDES`
- [x] Fixed `build/pelican_builder.py` to read `THEME_TEMPLATE_OVERRIDES`
- [x] Removed `@pytest.mark.skip` from E2E test
- [x] E2E test shows Pelican shared components now working, Galleria template precedence issue remains
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Fix: Complete THEME_TEMPLATE_OVERRIDES alignment`

**CRITICAL BLOCKER - Fix Test Pollution Before Phase 5B** ✅ **RESOLVED** 

*Problem: E2E tests were writing to production paths instead of isolated temporary directories, polluting the real codebase with build artifacts*

**Root Cause Identified**: Tests/commands run from `config/` directory with relative paths in config files caused `config/output/` pollution.

- [x] **Clean up git tree FIRST**
  - [x] Remove all built files from git tracking: `config/output/` (commit 7785253)
  - [x] Update .gitignore to prevent future pollution (`config/output/` already included)
  - [x] Verify no other test artifacts in version control
  - [x] Commit cleanup immediately (commit 7785253)

- [x] **Then investigate test isolation failure**
  - [x] Find why tests write to `config/output/` instead of temp dirs (relative paths + wrong working directory)
  - [x] Check `temp_filesystem` fixture usage in shared component tests (properly isolated)
  - [x] Verify build processes use proper temporary directory isolation (confirmed working)
  - [x] Document root cause of test pollution (CHANGELOG.md 2025-12-18)
  
- [x] **Fix test isolation**
  - [x] Ensure ALL E2E tests use proper temporary directory isolation (verified working)
  - [x] Fix build processes to never write to production paths during tests (not needed - already isolated)
  - [x] Add safeguards to prevent test pollution (`.gitignore` updated)
  - [x] Verify shared component tests run in complete isolation (confirmed working)

**RESOLUTION**: Test pollution was caused by running commands from wrong directory with relative config paths. All tests are properly isolated using `temp_filesystem` fixture. `.gitignore` prevents future pollution.

**Phase 5B: Manual Integration Verification** (Only after test pollution fixed)

#### Task 5.1.1: Fix Pelican Theme Override Configuration (Branch: fix/shared-components)

*Problem Statement: Pelican completely ignores custom theme configuration despite proper setup. The builder incorrectly replaces the primary theme with shared template override path, causing shared component integration failure and duplicate navbars.*

**Phase 1: Setup & E2E Definition** ✅ **COMPLETED**
- [x] E2E test exists in `test/e2e/test_shared_navbar_integration.py`
- [x] Test currently passes due to workarounds, needs updating to detect the real issues

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Update Integration Test to Detect Issues* ✅ **COMPLETED**
- [x] Update test to use correct config setting name (`THEME_TEMPLATES_OVERRIDES` plural)
- [x] Add proper custom theme structure in test (`themes/site/templates/base.html`)
- [x] Remove content workaround (`{% include 'navbar.html' %}` from content files)
- [x] Add duplicate navbar detection (count occurrences of navbar ID)
- [x] Test should fail, proving it can detect the current broken implementation
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Update test for Pelican override issues`

*Cycle 2: Fix Configuration Setting Name* ✅ **COMPLETED**
- [x] Update `config/pelican.json`: `THEME_TEMPLATE_OVERRIDES` → `THEME_TEMPLATES_OVERRIDES`
- [x] Update `config/galleria.json`: Same change for consistency
- [x] Update `build/pelican_builder.py`: Check for correct plural setting name
- [x] Tests should still fail due to theme override logic issues
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Fix: Use plural THEME_TEMPLATES_OVERRIDES setting`

*Cycle 3: Fix PelicanBuilder Theme Override Logic* ✅ **COMPLETED**
- [x] Remove line 136 that incorrectly overrides THEME setting
- [x] Keep original `THEME = themes/site` setting preserved
- [x] Set `THEME_TEMPLATES_OVERRIDES` as list for template search paths
- [x] Copy shared CSS to theme static directory before build
- [x] Pelican tests now pass - custom theme with shared navbar working!
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Fix: Preserve primary theme with overrides`

*Cycle 4: Update Production Theme Structure* ✅ **COMPLETED**
- [x] Update `themes/site/templates/base.html` to include shared navbar (already correct)
- [x] Remove workaround `{% include 'navbar.html' %}` from `content/index.md`
- [x] Ensure proper HTML structure matches test expectations
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Fix: Remove content navbar workarounds`

*Cycle 5: Fix Configuration Schema Validation* ⚠️ **BLOCKING**
- [ ] Update `config/schema/galleria.json`: Change `THEME_TEMPLATE_OVERRIDES` → `THEME_TEMPLATES_OVERRIDES`
- [ ] Test config validation passes: `uv run site validate`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Fix: Update schema for plural THEME_TEMPLATES_OVERRIDES setting`

*Cycle 6: Fix Galleria Shared Template Integration*
- [ ] Debug why Galleria isn't showing shared navbar (test fails line 150)
- [ ] Check Galleria template plugin and shared template loading
- [ ] Fix Galleria `THEME_TEMPLATES_OVERRIDES` configuration
- [ ] Integration test should pass completely (both Pelican AND Galleria)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Fix: Complete Galleria shared template integration`

**Phase 3: Comprehensive Manual Verification**
- [ ] **Full build verification**: `uv run site build` (must succeed)
- [ ] **Shared component verification**: 
  - [ ] Identical shared navbar in both `/` and `/galleries/wedding/`
  - [ ] Shared CSS consistent across both systems
  - [ ] Exactly 1 navbar per page (no duplicates)
- [ ] **Gallery functionality verification**:
  - [ ] Gallery link `/galleries/wedding/` works from home
  - [ ] Thumbnails display correctly in gallery grid
  - [ ] Clicking thumbnails opens full-size images
  - [ ] Gallery pagination works, navigation back to home works
- [ ] **Full test suite passes**: Zero failing tests before manual verification
- [ ] Update `doc/architecture.md` with corrected integration patterns
- [ ] Update `doc/modules/galleria/themes.md` with proper configuration
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Update shared component integration documentation`

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

### Performance Optimizations  

- [ ] Gallery lazy loading with JS progressive enhancement
- [ ] Parallel thumbnail processing and incremental generation
- [ ] WebP compression optimization
- [ ] Dark mode toggle (CSS variables + minimal JS)

### Shared Component Enhancements

- [ ] **Context-Aware Shared Header**: Replace separate site titles with smart shared header that adapts based on system context
  - **Pattern**: `{% if collection_name %}Gallery: {{ collection_name }}{% elif SITENAME %}{{ SITENAME }}{% endif %}`  
  - **Pelican context**: `SITENAME`, `SITEURL`, `article.title`
  - **Galleria context**: `collection_name`, `page_num`, `total_pages`, `photos|length`
  - **Location**: Create `themes/shared/templates/header.html`, replace both systems' headers
  - **Result**: Consistent header styling with appropriate context (site name vs gallery name)

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
