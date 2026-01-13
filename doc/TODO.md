# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

For detailed planning guidance, templates, and examples, see: **[`PLANNING.md`](PLANNING.md)**

## MVP Roadmap

### Phase 7: Performance Benchmarking (Branch: opt/benchmark)

*Goal: Collect hard numbers to guide post-MVP optimization priorities*

#### Metric Categories

**UX/Frontend Metrics (Browser-side):**
- Core Web Vitals: LCP, FID/INP, CLS
- Loading Timeline: TTFB, FCP, TTI
- Page Weight: Total HTML size, CSS size, thumbnail payload per page
- Lighthouse Scores: Performance, Accessibility, Best Practices
- Pagination Impact: Measure all above at photos_per_page: 20, 50, 100, 150, 200, 300, 500

**Build/Generation Metrics (Pipeline-side):**
- Pipeline Stage Timing: validate, organize, build durations
- Thumbnail Processing: Time per photo, batch throughput, output file sizes (galleria - keep decoupled)
- Gallery Generation: Time per collection, total build time, memory usage
- Output Sizes: HTML per page, total CSS, manifest sizes

#### Collection Methodology

- **UX Metrics**: Lighthouse CLI (npm dependency), `lighthouse <url> --output=json`
- **Build Metrics**: `--benchmark` flag on pipeline commands, `site benchmark` convenience command
- **Output**: JSON to `/.benchmarks/` (gitignored), curated results to `doc/benchmark/results/`

#### Task 7.0: Branch Setup & Planning

- [ ] `git checkout -b opt/benchmark`
- [ ] Update `doc/TODO.md` with finalized performance benchmark plan
- [ ] Commit: `Pln: Update TODO with performance benchmarking tasks`

#### Task 7.1: Manual Baseline Collection

*Collect initial metrics for wedding gallery before implementing automation*

- [ ] Install Lighthouse CLI: `npm install -g lighthouse`
- [ ] Create `doc/benchmark/` directory structure
- [ ] Create `doc/benchmark/README.md` with methodology documentation
- [ ] Run manual baseline collection:
  - [ ] Time pipeline stages with `time` wrapper
  - [ ] Run Lighthouse against production wedding gallery
  - [ ] Record thumbnail sizes, page weights, file counts
- [ ] Create `doc/benchmark/results/YYYY-MM-DD_baseline.json` with results
- [ ] Hand-edit metadata (commit, description, config, notes)
- [ ] Write `doc/benchmark/baseline.md` with analysis
- [ ] Commit: `Doc: Add performance baseline for wedding gallery`

#### Task 7.2: Add Benchmark Infrastructure

*Top-level `site benchmark` command drives --benchmark flag implementation for each subcommand*

**Setup & E2E Definition**

- [ ] Add `/.benchmarks/` to `.gitignore`
- [ ] Create E2E test in `test/e2e/test_benchmark_command.py`
  - [ ] Test `site benchmark` runs full pipeline with benchmark instrumentation
  - [ ] Test outputs results to `/.benchmarks/`
  - [ ] Test output includes metrics from each stage (validate, organize, build)
  - [ ] Add `@pytest.mark.skip("Benchmark command not implemented")`
- [ ] Create separate test module `test/galleria/test_thumbnail_benchmark.py`
  - [ ] Test thumbnail encode timing metrics (time per photo, batch throughput)
  - [ ] Test thumbnail output size metrics
  - [ ] Keep isolated for future galleria extraction
  - [ ] Add `@pytest.mark.skip("Thumbnail benchmarking not implemented")`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Tst: Add E2E tests for benchmark infrastructure (skipped)`

**TDD Implementation**

*Benchmark output structure:*
- [ ] Write unit test for benchmark result dataclass/schema
- [ ] Implement `BenchmarkResult` class with metadata and metrics fields
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add BenchmarkResult data structure`

*Timing instrumentation:*
- [ ] Write unit test for timing context manager/decorator
- [ ] Implement timing utility that captures duration and memory
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add benchmark timing instrumentation`

*Add --benchmark flag to validate command:*
- [ ] Write unit test for validate command with --benchmark flag
- [ ] Implement `--benchmark` flag on `site validate`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add --benchmark flag to validate command`

*Add --benchmark flag to organize command:*
- [ ] Write unit test for organize command with --benchmark flag
- [ ] Implement `--benchmark` flag on `site organize`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add --benchmark flag to organize command`

*Thumbnail encoding instrumentation (galleria):*
- [ ] Write unit test in `test/galleria/test_thumbnail_benchmark.py`
- [ ] Instrument thumbnail encoding in galleria (time per photo, sizes)
- [ ] Ensure metrics surface through build command
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add thumbnail encoding benchmark instrumentation`

*Add --benchmark flag to build command:*
- [ ] Write unit test for build command with --benchmark flag
- [ ] Implement `--benchmark` flag on `site build`
- [ ] Include thumbnail metrics from galleria
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add --benchmark flag to build command`

*Implement site benchmark command:*
- [ ] Write unit test for benchmark command orchestration
- [ ] Implement `site benchmark` that runs cascade with `--benchmark`
- [ ] Aggregate results from each stage into single output file
- [ ] Output to `/.benchmarks/`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Ft: Add site benchmark command`

**Integration & Documentation**

- [ ] Remove `@pytest.mark.skip` from E2E tests
- [ ] Verify E2E tests pass
- [ ] Update `doc/benchmark/README.md` with usage instructions
- [ ] Document workflow: `site benchmark` → annotate → copy to `doc/benchmark/results/`
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Commit: `Doc: Document benchmark infrastructure`

**Validation Against Manual Baseline**

- [ ] Run `site benchmark` against wedding gallery (clean build)
- [ ] Compare automated results with `doc/benchmark/results/2026-01-13_baseline.json`
- [ ] Verify build metrics match within acceptable variance (~5%)
- [ ] Document any discrepancies and their causes
- [ ] Commit: `Tst: Validate benchmark infrastructure against manual baseline`

#### Task 7.3: Pagination Performance Comparison

*Test UX metrics across different photos_per_page values*

- [ ] Create test galleries with photos_per_page: 20, 50, 100, 150, 200, 300, 500
- [ ] Run Lighthouse against each variant
- [ ] Record results in `/.benchmarks/` initially
- [ ] Copy annotated results to `doc/benchmark/results/`
- [ ] Write `doc/benchmark/pagination.md` with comparison analysis
- [ ] Document optimal photos_per_page recommendation
- [ ] Commit: `Doc: Add pagination performance comparison`

#### Task 7.4: PR Creation

- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Verify all tests pass
- [ ] `gh pr create --title "Opt: Add performance benchmarking infrastructure" --body "..."`

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

- [ ] **Edge Rules Production Finalization**
  - [ ] Change Edge Rules from 302 temporary to 301 permanent redirects after monitoring production stability

- [ ] **Version 0.1.0 Release Finalization**
  - [ ] Final ruff/pytest run across entire codebase (target: 0 failures)
  - [ ] Update version numbers in relevant files
  - [ ] Create final commit with version bump and release notes
  - [ ] Tag release v0.1.0

## Post-MVP Enhancements

#### Task: Add CDN Cache Purge Command

- [ ] Research full Bunny.net API cache management capabilities: tag-based purging (<1s global), wildcard patterns (/galleries/wedding/*), individual URL purging, and other API features that might better suit our deployment patterns
- [ ] Implement `uv run site purge` command with targeted cache invalidation options

#### Task 5.2: Mobile-First Responsive Layout (Branch: ft/responsive-layout)

*Problem Statement: Site lacks mobile optimization with poor touch targets, non-responsive gallery grid, and inconsistent mobile experience across page types.*

**Initial Setup & E2E Test Definition**

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

**TDD Implementation Cycles**

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
- [ ] Basic
- [ ] Parallel thumbnail processing and incremental generation
- [ ] Dark mode toggle (CSS variables + minimal JS)
- [ ] WebP compression optimization
- [ ] **Deployment Metrics** *(requires planning task before implementation)*
  - [ ] Upload volume analysis (files changed vs total, bytes transferred)
  - [ ] CDN performance analysis (cache hits, edge response times)
  - [ ] Lighthouse testing against CDN for production UX metrics

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
