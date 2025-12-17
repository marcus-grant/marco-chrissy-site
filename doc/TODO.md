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


### Phase 5: Site Navigation & Layout Integration

*Problem Statement: Site lacks cohesive navigation between Pelican static pages and Galleria gallery pages, resulting in inconsistent styling and poor user experience. Users cannot easily navigate between static content (/about/) and galleries (/galleries/wedding/), and the two systems use completely separate CSS frameworks with no visual consistency.*

#### Task 5.1: Shared Theme Component Foundation (Branch: ft/shared-components)

*Problem Statement: Site needs unified theme system to share assets, templates, and components between Pelican and Galleria without tight coupling for future Galleria extraction.*

**Phase 1: Setup & E2E Definition**
- [x] `git checkout -b ft/shared-components`
- [x] Create E2E test in `test/e2e/test_shared_components.py`
  - [x] Test that both Pelican and Galleria can load shared assets and templates
  - [x] Verify PicoCSS loads consistently across page types
  - [x] Test shared template inclusion from both systems
  - [x] Add `@pytest.mark.skip("Shared component system not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for shared component system (skipped)`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Create Shared Asset Management*
- [x] Create `themes/shared/` directory structure
- [x] Write unit test for asset manager utility that fails
- [x] Implement `themes/shared/utils/asset_manager.py` for external dependencies
- [x] Download PicoCSS to `output/css/pico.min.css` during build
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add shared asset manager with PicoCSS integration`

*Cycle 2: Implement Shared Template Search Paths*
- [x] Write unit test for template loader configuration that fails
- [x] Update Pelican Jinja2 loader to include `themes/shared/templates/`
- [x] Update Galleria template system to include shared template paths
- [x] Create example shared template to verify functionality
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Configure shared template search paths for both systems`

*Cycle 3: Create Context Adapter Pattern*
- [ ] Write unit test for context adapter interface that fails
- [ ] Create `themes/shared/utils/context_adapters.py` with base interface
- [ ] Implement Pelican context adapter for shared templates
- [ ] Implement Galleria context adapter for shared templates
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Implement context adapters for template compatibility`

**Phase 3: Integration & Documentation**
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes (if not, return to Phase 2)
- [ ] Update `doc/architecture.md` with shared component architecture
- [ ] Create `doc/future/galleria-extraction.md` with dependency injection patterns
- [ ] Update `doc/modules/galleria/themes.md` with new template system
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Document shared component architecture and extraction patterns`

**Phase 4: PR Creation**
- [ ] `gh pr create --title "Ft: Implement shared theme component foundation" --body "Establishes unified system for sharing assets, templates, and components between Pelican and Galleria with future-ready extraction patterns"`

#### Task 5.2: Unified Navigation Component (Branch: ft/unified-nav)

*Problem Statement: Users cannot navigate cohesively between static pages and galleries due to independent navigation systems with no cross-system linking.*

**Phase 1: Setup & E2E Definition**
- [ ] `git checkout -b ft/unified-nav`
- [ ] Create E2E test in `test/e2e/test_unified_navigation.py`
  - [ ] Test navigation appears consistently on all page types (static and gallery)
  - [ ] Verify navigation links work between Pelican and Galleria pages
  - [ ] Test active state highlighting for current page/section
  - [ ] Test responsive navigation behavior at different screen sizes
  - [ ] Add `@pytest.mark.skip("Unified navigation not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Add E2E test for unified navigation (skipped)`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Create Shared Navigation Configuration*
- [ ] Write unit test for navigation configuration loading that fails
- [ ] Create `config/navigation.json` with primary nav and gallery context
- [ ] Update site configuration loading to include navigation config
- [ ] Implement navigation config validation
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add navigation configuration structure`

*Cycle 2: Build Shared Navigation Templates*
- [ ] Write unit test for navigation template rendering that fails
- [ ] Create `themes/shared/templates/navigation/` directory
- [ ] Implement `base.html`, `primary.html`, `breadcrumbs.html` templates
- [ ] Add responsive design with mobile-first approach
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Create shared navigation templates with responsive design`

*Cycle 3: Integrate Navigation into Pelican*
- [ ] Write unit test for Pelican navigation integration that fails
- [ ] Create custom Pelican theme inheriting from "simple"
- [ ] Update Pelican `base.html` to include shared navigation templates
- [ ] Implement Pelican context adapter for navigation data
- [ ] Test navigation active states for static pages
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Integrate shared navigation into Pelican pages`

*Cycle 4: Integrate Navigation into Galleria*
- [ ] Write unit test for Galleria navigation integration that fails
- [ ] Update Galleria templates to include shared navigation
- [ ] Implement Galleria context adapter for navigation data
- [ ] Add breadcrumb navigation for gallery context (Home > Galleries > Wedding)
- [ ] Test navigation works with gallery URL structure
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Integrate shared navigation into Galleria pages`

**Phase 3: Integration & Documentation**
- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes (if not, return to Phase 2)
- [ ] Update `doc/configuration.md` with navigation configuration options
- [ ] Update `doc/modules/galleria/themes.md` with template inheritance patterns
- [ ] Document responsive navigation patterns in architecture docs
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Update navigation and template integration documentation`

**Phase 4: PR Creation**
- [ ] `gh pr create --title "Ft: Implement unified navigation across all pages" --body "Creates consistent navigation experience between static content and gallery pages with responsive design and proper context awareness"`

#### Task 5.3: Mobile-First Responsive Layout (Branch: ft/responsive-layout)

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
