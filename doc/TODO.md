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
