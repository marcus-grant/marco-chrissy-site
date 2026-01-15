# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md).
This ensures consistent,
high-quality development that naturally follows the workflow rules in
[`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in
following our development workflow.

**Before adding or modifying tasks** (beyond marking items complete):
Read [`PLANNING.md`](PLANNING.md)
for guidance on task structure, templates, and examples.

**Workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md)
must always be respected** when working on this project.

## Post-MVP Enhancements

### Performance Optimizations

*Split into frontend and backend PRs. Each requires benchmarking before/after using Lighthouse (frontend) and built-in benchmarking (backend). Analyze page sizes, load times, and generation metrics. Full planning for each PR happens separately.*

**Version bump**: Minor version (0.3.0) after both backend and frontend PRs complete.

#### Backend Performance (Branch: `ft/parallel-thumbnails`) - COMPLETE

*Problem Statement: Thumbnail processing is sequential (~421s for 645 photos). Need parallel processing for speedup, per-photo benchmarking for metrics, and quality analysis to find optimal WebP settings.*

*Testing: All tests use existing fixtures (`galleria_temp_filesystem`, `galleria_image_factory`, `galleria_file_factory`, `config_file_factory`) - no real filesystem access.*

**Setup & E2E Definition**

- [x] `git checkout -b ft/parallel-thumbnails`
- [x] Create E2E test in `test/e2e/test_parallel_thumbnails.py`
  - [x] Test parallel processing generates all thumbnails
  - [x] Test benchmark metrics captured in result metadata
  - [x] Add `@pytest.mark.skip("Parallel processing not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Tst: Add E2E test for parallel thumbnails (skipped)`

**TDD Implementation**

*ThumbnailBenchmark Class*

- [x] Unskip tests in `test/galleria/test_thumbnail_benchmark.py`
- [x] Create `galleria/benchmark.py` with `ThumbnailBenchmark` dataclass
  - [x] `record_photo(duration_s, output_bytes)` method
  - [x] `get_metrics()` returns `per_photo_times`, `photos_per_second`, `output_sizes`, `average_output_bytes`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Ft: Add ThumbnailBenchmark class`

*Extract Single-Photo Processing*

- [x] Extract for-loop body from `thumbnail.py:124-194` into `_process_single_photo()` function
  - [x] Top-level function (required for ProcessPoolExecutor pickling)
  - [x] Returns dict with `thumbnail_path`, `thumbnail_size`, `cached`, or `error`
- [x] Add unit tests in `test/galleria/unit/plugins/test_thumbnail_processor.py`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Ref: Extract single-photo processing function`

*Parallel Config Options*

- [x] Add config parsing in `process_thumbnails()`:
  - [x] `parallel: bool` (default `False`)
  - [x] `max_workers: int | None` (default `os.cpu_count()`)
- [x] Add unit tests for config parsing
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Ft: Add parallel processing config options`

*Parallel Processing Implementation*

- [x] Add parallel path using `concurrent.futures.ProcessPoolExecutor`
  - [x] Use `as_completed()` for progress tracking
  - [x] Sequential path unchanged when `parallel=False`
- [x] Create integration tests in `test/galleria/integration/test_thumbnail_processor_parallel.py`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Ft: Implement parallel thumbnail processing`

*Benchmark Integration*

- [x] Add `benchmark: bool` config option (default `False`)
- [x] Capture per-photo timing and sizes when enabled
- [x] Return metrics in `result.output_data["benchmark"]`
- [x] Add unit tests for benchmark integration
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Ft: Integrate ThumbnailBenchmark with processor`

**Integration & E2E Verification**

- [x] Remove `@pytest.mark.skip` from E2E test
- [x] Verify E2E test passes
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Commit: `Tst: Enable parallel thumbnails E2E test`

**Quality Analysis**

- [ ] Run benchmarks at quality levels 60, 70, 80, 90 *(manual)*
- [ ] Collect encode times and file sizes *(manual)*
- [ ] Select 3 sample photos, host externally *(manual)*
- [ ] Run sequential baseline benchmark *(manual)*
- [ ] Run parallel scaling tests (1, 2, 4, 8, 16 workers) *(manual)*
- [x] Create `doc/benchmark/quality-analysis.md` with template structure
- [x] Commit: `Doc: Add WebP quality analysis`

**Documentation Update**

- [x] Update `doc/CHANGELOG.md` with PR changes
- [x] Update `doc/benchmark/README.md` to link quality-analysis.md
- [x] Mark Backend Performance items complete in this file
- [x] Commit: `Doc: Update docs for backend performance`

**Version & PR**

- [ ] Update version in `pyproject.toml`: 0.2.1 → 0.2.2
- [ ] Commit: `Ft: Bump version to 0.2.2`
- [ ] `gh pr create --title "Ft: Parallel thumbnail processing with quality analysis"`

#### Frontend Performance (separate PR)

- [ ] Improve benchmarking infra to include lighthouse runner and metrics collection
- [ ] Gallery lazy loading with JS progressive enhancement
- [ ] Dark mode toggle (CSS variables + minimal JS)
- [ ] Lighthouse benchmarks before/after
- [ ] Improve typography and spacing for readability

### Extra Frontend Enhancements

- [ ] Improve typography (font choices, sizes, line heights)
- [ ] Add more containers for elements to improve spacing and layout
  - [ ] Index page looks like shit, at least add containers for text there
  - [ ] Margins of thumbnails or padding could use work.
- [ ] Navbar improvements
  - [ ] Home link should be our names
  - [ ] links should be separated differently
  - [ ] Landing page already does 'About' page's role
  - [ ] Should be a 'Links' or 'Our Links' or something page with link
    - Contains our links to reach us on other sites or platforms or email
    - Think of it like a linktr.ee type page
- Start making better use of color, I don't know exactly where yet though
- Add a basic favicon, maybe a simple heart, maybe with our initials or something

### Confusion

- Here I'm less sure how to order things
- Should we create another performance check before adding 'web-optimized' images?
  - Includes setting up a mirror set of images of same content with normpic:
    - but different sizes/qualities for other use cases:
      - *(thumbnails, web-optimized, full-res)*
- If we do this we should also be backing up our changes with benchmarks
- Add full-sized views of images clicked on thumbnails using web-opt images
  - This means we need a means to show the full sized ones or download them

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

#### Deployment Metrics *(requires planning task before implementation)*

- [ ] Upload volume analysis (files changed vs total, bytes transferred)
- [ ] CDN performance analysis (cache hits, edge response times)
- [ ] Lighthouse testing against CDN for production UX metrics

### Code Quality

- [ ] Comprehensive error handling for plugin failures
- [ ] Verify galleria idempotency behavior and manifest-based change detection
- [ ] Enhanced fake image fixtures for EXIF testing
- [ ] Remove dead code (old manifest serializer, thumbnail processor)
- [ ] **Rename build/ to builders/**: Directory conflicts with Python's `build/` artifact directory in `.gitignore`. Rename module and update all imports.

### Medium-term Features

- [ ] **External Asset Version Pinning**: Add version control for reproducible builds (config-based pinning with integrity hashes vs lock files) - update themes/shared/utils/asset_manager.py

#### Galleria Extraction Preparation

- [ ] Independence audit (remove parent project dependencies)
- [ ] Technical debt cleanup (type hints, error handling, performance)
- [ ] Evaluate shared schema package with NormPic
- [ ] **Complete `galleria/serializer/` typed models**: Currently incomplete - `Photo`, `PhotoCollection` models exist but plugin system uses dicts. For extraction, either:
  - Have `NormPicProviderPlugin` return typed models instead of dicts, or
  - Remove serializer and keep dict-based plugin contract
- [ ] Plan the procedure to extract Galleria as standalone project
  - [ ] Come up with list of files containing Galleria code, tests, docs
  - [ ] Testable plan to prove imported galleria package works in parent project
  - [ ] Plan how to keep main branch safe during extraction
  - [ ] Plan to pull git history into new repo

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
- [ ] Change Edge Rules from 302 temporary to 301 permanent redirects
- [ ] **Cache-Busting for Static Assets**: Add version/hash to CSS/JS filenames to avoid stale browser cache
  - Planning: evaluate query string (`?v=X.Y.Z`) vs hashed filenames (`shared.a1b2c3.css`)
  - Consider build manifest to track current vs old files for storage cleanup
  - Integrate with `site purge` command for old file removal from CDN + storage

#### Long-term Considerations

- [ ] FastAPI/Django/Wagtail integration for dynamic features
- [ ] API endpoints for gallery data
- [ ] Galleria advanced features: video support, RAW processing, cloud storage, GUI tools

## Future Architecture Planning

Post-MVP modularization strategy documented in [Future Architecture](future/). Key goals:

- Create **SnakeCharmer** framework for multi-paradigm site orchestration
  - Python-based orchestrator that coordinates SSG, APIs, micro frontends, and CDN deployment
  - Manages the "menagerie" of tools: Galleria, Cobra, FastAPI, Bunny CDN, etc.
  - CLI: `uv run snakecharmer build`, `uv run snakecharmer serve`, `uv run snakecharmer deploy`
  - Abstract builder interfaces from day one (SSG, API, frontend builders)
  - Site-specific content, templates, CSS, configs live in each site's repo
  - SnakeCharmer imported as a package dependency
- Create **Cobra** as Pelican replacement
  - Python-based SSG inspired by 11ty's architecture
  - Simpler, less opinionated than Pelican
  - Integrates as a builder within SnakeCharmer
- Enable endpoint abstraction (same logic → static/FastAPI/HTMX/edge functions)
- Transform this repo to configuration/deployment hub

### SnakeCharmer Extraction Preparation

- [ ] Define abstract Builder interface for SSG, API, and frontend builders
- [ ] Extract orchestration code (cli/, build/, serve/, deploy/, validator/, serializer/)
- [ ] Design configuration discovery (convention-based vs pyproject.toml entry points)
- [ ] Plan hook system for site-specific customizations
- [ ] Create new SnakeCharmer repo and migrate orchestration code
- [ ] Update this repo to import SnakeCharmer as dependency
- [ ] Test that marco-chrissy-site works with extracted SnakeCharmer

### Cobra Development

- [ ] Research 11ty architecture patterns to adapt for Python
- [ ] Design simpler, less opinionated template/content model than Pelican
- [ ] Implement Cobra as standalone package
- [ ] Create CobraBuilder for SnakeCharmer integration
- [ ] Migrate marco-chrissy-site from Pelican to Cobra

## Notes

- Maintain non-JS functionality as primary requirement
- All enhancements must use progressive enhancement
- Performance metrics before and after each optimization
- Keep Galleria extractable for future open-sourcing
- Design plugin interface from day one - modularity is foundational
- Plugin hooks should be lightweight and clearly defined
- Each component should be pluggable without tight coupling
