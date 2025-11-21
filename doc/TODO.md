# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development - ✅ COMPLETED

**Status Summary:**

- [x] Complete 5-stage plugin system implemented
- [x] CLI `generate` command with 239 passing E2E tests  
- [x] Production-ready gallery generation functionality
- [x] Comprehensive documentation and workflow guides

### Phase 2: Site Structure

**Architecture:** 4-stage idempotent pipeline with plugin-based Pelican integration

#### 2.1: Project Structure Setup
- [x] Create test structure (`test/e2e/` and `test/unit/`)
- [ ] Create root-level module directories
  - [ ] `validator/` - Pre-flight checks (configs, dependencies, permissions)
  - [ ] `build/` - Orchestration modules (Galleria + Pelican coordination)
  - [ ] `deploy/` - Bunny CDN upload logic
  - [ ] `cli/` - Command-line interface with subcommands
  - [ ] `serializers/` - JSON config loading with schema validation

#### 2.2: CLI Command System (Idempotent Cascading)
- [ ] E2E test: `uv run site` command discovery and basic functionality (`test/e2e/`)
- [ ] Unit tests: Individual command modules (`test/unit/`)
- [ ] Implement `uv run site` command with subcommands
  - [ ] `site validate` - Pre-flight checks, lazy execution
  - [ ] `site organize` - NormPic orchestration (calls validate if needed)
  - [ ] `site build` - Galleria + Pelican generation (calls organize if needed)  
  - [ ] `site deploy` - Bunny CDN upload (calls build if needed)
- [ ] Each command checks if work already done and skips unnecessary operations

#### 2.3: Configuration Architecture (Separate Configs)
- [ ] E2E test: Config loading and validation across modules (`test/e2e/`)
- [ ] Unit tests: JSON serializer and schema validation (`test/unit/serializers/`)
- [ ] Create JSON serializer/schema system in `serializers/json.py`
- [ ] Create config files with JSON schemas:
  - [ ] `config/site.json` - Orchestration, output paths, Bunny CDN deployment
  - [ ] `config/normpic.json` - Photo organization settings for wedding collection
  - [ ] `config/pelican.json` - Site page generation (theme, content paths, URLs)
  - [ ] Update existing `config/galleria.json` for wedding gallery
- [ ] Config schemas in `config/schemas/` for validation

#### 2.4: Pelican + Galleria Integration (Plugin-Based)
- [ ] E2E test: Complete plugin-based gallery generation workflow (`test/e2e/`)
- [ ] Unit tests: PelicanTemplatePlugin functionality (`test/unit/plugins/`)
- [ ] Create `PelicanTemplatePlugin` extending Galleria's `TemplatePlugin`
  - [ ] Plugin uses shared Jinja2 templates for consistent navigation/styling
  - [ ] Configure Galleria to use `PelicanTemplatePlugin` instead of `BasicTemplatePlugin`
  - [ ] Maintain Galleria extractability - site-specific logic stays in plugin
- [ ] Set up Pelican with coordinated theme system
  - [ ] Shared template files for navigation/layout components
  - [ ] Configure Pelican theme to match Galleria styling

#### 2.5: Content Pages & Output Structure
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
- [ ] Set up dual CDN deployment strategy (photos vs site content)

### Phase 3: Integration Testing

- [ ] Test command system end-to-end
- [ ] Validate site generation workflow
- [ ] Test Galleria + Pelican integration

### Phase 4: Performance Baseline

- [ ] Measure initial performance metrics
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

## Post-MVP Enhancements

### Near-term Optimizations

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
  - [ ] Anything else
- [ ] Add Christmas gallery
- [ ] Add vacation gallery

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
  - [ ] Document Galleria-only installation process
- [ ] Galleria technical debt cleanup
  - [ ] **CRITICAL**: Unify plugin configuration access patterns
    - [ ] Remove dual config pattern support (nested vs direct)
    - [ ] Standardize on single config approach across all plugins
    - [ ] Update all unit tests to use unified config pattern
    - [ ] Remove backward compatibility config detection code
    - [ ] Choose either: nested stage-specific OR flattened direct access
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
