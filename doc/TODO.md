# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

**Before adding or modifying tasks** (beyond marking items complete): Read [`PLANNING.md`](PLANNING.md) for guidance on task structure, templates, and examples.

**Workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md) must always be respected** when working on this project.

## Post-MVP Enhancements

#### Task: Add CDN Cache Purge Command

- [ ] Research full Bunny.net API cache management capabilities: tag-based purging (<1s global), wildcard patterns (/galleries/wedding/*), individual URL purging, and other API features that might better suit our deployment patterns
- [ ] Implement `uv run site purge` command with targeted cache invalidation options

#### Task: Mobile-First Responsive Layout (Branch: ft/responsive)

*Problem Statement: Site lacks mobile optimization with poor touch targets, non-responsive gallery grid, and inconsistent mobile experience across page types.*

**Breakpoints & Grid Columns:**
- Default: 2 columns (mobile)
- 560px: 3 columns (large phone / small tablet)
- 768px: 4 columns, navbar collapses to hamburger (tablet)
- 1024px: 6 columns (desktop)

*Rationale: 96 photos/page divides evenly by 2, 3, 4, 6 for clean row layouts*

**Initial Setup & E2E Test Definition**

- [x] Create E2E test in `test/e2e/test_responsive_layout.py`
  - [x] Test CSS variables exist (breakpoints, touch-target sizes)
  - [x] Test gallery grid adapts 1→2→3→4→6 columns at breakpoints
  - [x] Test touch targets meet 44px minimum requirement
  - [x] Test navbar has mobile menu structure (CSS-only checkbox hack)
  - [x] Test responsive typography uses clamp()
  - [x] Add `@pytest.mark.skip("Responsive layout not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Add E2E test for responsive layout (skipped)`

**TDD Implementation**

*CSS Foundation - Variables and Breakpoints*

- [x] Write unit test for CSS variables in `test/unit/test_shared_css.py`
- [x] Add `:root` block to `themes/shared/static/css/shared.css`:
  - `--breakpoint-sm: 480px`, `--breakpoint-md: 768px`, `--breakpoint-lg: 1024px`, `--breakpoint-xl: 1200px`
  - `--touch-target-min: 44px`
  - Spacing variables (`--spacing-xs` through `--spacing-lg`)
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add CSS variables for responsive breakpoints`

*Responsive Navbar with CSS-Only Mobile Menu*

- [x] Write unit test for navbar HTML structure (checkbox toggle)
- [x] Write unit test for navbar CSS media queries
- [x] Update `themes/shared/templates/navbar.html` with mobile structure:
  - Checkbox input + label for toggle (accessibility)
  - `.nav-links` container for hideable links
- [x] Update `themes/shared/static/css/shared.css` with responsive navbar
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add CSS-only responsive mobile navbar`

*Touch-Friendly Navbar Sizing*

- [x] Write unit test for navbar touch target sizing
- [x] Update navbar links with `min-height: var(--touch-target-min)`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: (included in responsive navbar commit)

*Mobile-First Gallery Grid*

- [x] Write unit test in `test/galleria/unit/plugins/test_css.py` for grid breakpoints
- [x] Update `galleria/plugins/css.py` `_generate_gallery_css()`:
  - Default: 2 columns, 560px: 3 columns, 768px: 4 columns, 1024px: 6 columns
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add mobile-first gallery grid (1→2→3→4→6)`

*Touch-Friendly Pagination*

- [x] Write unit test for pagination touch target sizing
- [x] Update pagination CSS: `min-height: 44px`, `min-width: 44px`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add touch-friendly pagination controls`

*Responsive Typography*

- [ ] Write unit test for `clamp()` in typography
- [ ] Update header: `font-size: clamp(1.5rem, 4vw + 0.5rem, 2.5rem)`
- [ ] Update body text with fluid sizing
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add responsive typography using CSS clamp()`

**Integration & Documentation**

- [ ] Remove `@pytest.mark.skip` from E2E test
- [ ] Verify E2E test passes (if not, return to TDD Implementation)
- [ ] Update `doc/testing.md` with responsive testing patterns
- [ ] Update `doc/architecture.md` with mobile-first design principles
- [ ] Document future JS enhancement plans in `doc/future/`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Doc: Add responsive design documentation`

**Manual Visual Verification**

- [ ] Run `uv run site serve` to start local development server
- [ ] Test at viewports: 320px (1 col), 480px (2 col), 768px (3 col), 1024px (4 col), 1200px (6 col)
- [ ] Verify navbar hamburger toggle works below 768px
- [ ] Verify touch targets feel adequate on mobile device
- [ ] Verify typography scales smoothly between viewport sizes

**PR Creation**

- [ ] `gh pr create --title "Ft: Implement mobile-first responsive layout" --body "..."`

### Performance Optimizations

- [ ] Gallery lazy loading with JS progressive enhancement
- [ ] Basic
- [ ] Parallel thumbnail processing and incremental generation
- [ ] Dark mode toggle (CSS variables + minimal JS)
- [ ] WebP compression optimization
- [ ] **Deployment Metrics** *(requires planning task before implementation)*
  - [ ] Upload volume analysis (files changed vs total, bytes transferred)
  - [ ] CDN performance analysis (cache hits, edge response times)
  - [ ] Lighthouse testing against CDN for production UX metrics

### Edge Rules Production Finalization

- [ ] Change Edge Rules from 302 temporary to 301 permanent redirects
  - Deferred until after purge command, responsive layout, and JS lazy loading to avoid browser caching issues

### Shared Component Enhancements

- [ ] **Context-Aware Shared Header**: Replace separate site titles with smart shared header that adapts based on system context
  - **Pattern**: `{% if collection_name %}Gallery: {{ collection_name }}{% elif SITENAME %}{{ SITENAME }}{% endif %}`  
  - **Pelican context**: `SITENAME`, `SITEURL`, `article.title`
  - **Galleria context**: `collection_name`, `page_num`, `total_pages`, `photos|length`
  - **Location**: Create `themes/shared/templates/header.html`, replace both systems' headers
  - **Result**: Consistent header styling with appropriate context (site name vs gallery name)

### Post-Frontend Enhancements Priority Issues

- [ ] **Build Idempotency**: Build regenerates all output files even when source unchanged, breaking incremental deploy
  - [ ] Build should only regenerate files when source files actually change
  - [ ] Preserve timestamps/hashes when content hasn't changed
  - [ ] Enable true incremental deploys (seconds instead of minutes for unchanged source)
  - [ ] Consider build manifest or file dependency tracking
- [ ] **Galleria Performance**: Optimize large photo collection processing (645+ photos cause CPU hang)
- [ ] **Eliminate Hardcoded Paths**: Create PathConfig class for dependency injection, remove `os.chdir()` calls
- [ ] **Plugin Output Validation**: Use structured types (Pydantic) instead of defensive CLI validation
- [ ] **E2E Test Performance**: Fix 16+ second subprocess startup time, consolidate tests

### Code Quality

- [ ] Comprehensive error handling for plugin failures
- [ ] Verify galleria idempotency behavior and manifest-based change detection
- [ ] Enhanced fake image fixtures for EXIF testing
- [ ] Remove dead code (old manifest serializer, thumbnail processor)
- [ ] **Rename build/ to builders/**: Directory conflicts with Python's `build/` artifact directory in `.gitignore`. Rename module and update all imports.

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
- [ ] **Complete `galleria/serializer/` typed models**: Currently incomplete - `Photo`, `PhotoCollection` models exist but plugin system uses dicts. For extraction, either:
  - Have `NormPicProviderPlugin` return typed models instead of dicts, or
  - Remove serializer and keep dict-based plugin contract

#### Long-term Considerations

- [ ] FastAPI/Django/Wagtail integration for dynamic features
- [ ] API endpoints for gallery data
- [ ] Galleria advanced features: video support, RAW processing, cloud storage, GUI tools

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
