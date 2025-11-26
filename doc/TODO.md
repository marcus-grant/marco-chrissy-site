# Marco & Chrissy's Website - TODO

## 🚨 CRITICAL ISSUES - FIX BEFORE MERGE

### Build Command Integration Breakage
The build command implementation is completely broken after attempting to replace subprocess calls with direct galleria module imports. **This PR is not ready for merge.**

**Issues created:**
- Build command fails in real usage due to incomplete Pelican configuration 
- All 9 unit tests in `test/unit/cli/test_build.py` are skipped (broken mock patterns)
- E2E test for build workflow is skipped due to Pelican setup errors
- Pelican integration needs proper theme system, content directories, and required settings
- Mock patterns need complete rewrite to match new import structure

**Impact:**
- `uv run site build` command is broken for actual usage
- Test coverage gap leaves integration untested
- Configuration system incomplete for Pelican workflow

**Next developer must:**
1. Fix Pelican configuration in build command (settings, themes, content structure)
2. Rewrite all unit test mocks for new direct import pattern 
3. Complete E2E test to verify full workflow
4. Test actual build command usage end-to-end
5. Remove skip decorators only after fixing underlying issues

**What we learned about Pelican requirements:**
- Pelican constructor requires a settings dict with ALL_CAPS keys
- Required settings: THEME, IGNORE_FILES, DELETE_OUTPUT_DIRECTORY (and others discovered during debugging)
- Must use `pelican.settings.configure_settings()` to get defaults rather than manual dict
- Needs existing content directory that `configure_settings()` can validate
- Theme must be valid theme name or path to existing theme directory
- Current pelican.json schema is insufficient - missing many required fields
- Pelican API is much more complex than initially assumed

## MVP Roadmap

### Phase 1: Galleria Development - ✅ COMPLETED

**Status Summary:**

- [x] Complete 5-stage plugin system implemented
- [x] CLI `generate` command with 239 passing E2E tests  
- [x] Production-ready gallery generation functionality
- [x] Comprehensive documentation and workflow guides

### Phase 2: Site Structure

**Architecture:** 4-stage idempotent pipeline with plugin-based Pelican integration

#### 2.2: CLI Command System (Idempotent Cascading)
- [x] E2E test: `uv run site` command discovery and basic functionality (`test/e2e/`)
- [x] Unit tests: Individual command modules (`test/unit/`)
- [x] Implement `uv run site` command with subcommands
  - [x] `site validate` - Pre-flight checks (config file validation implemented)
  - [x] `site organize` - NormPic orchestration (real integration implemented)
  - [x] `site build` - Galleria + Pelican generation (calls organize if needed)
    - [x] E2E test: Complete build pipeline with fake filesystem and images
    - [x] Unit tests: Build command integration (organize cascade, Python modules)
    - [x] Centralize fake image generation into shared fixtures
    - [x] Implement build command with galleria and pelican integration
    - [x] Verify BeautifulSoup validation of generated HTML content
    - [x] Test idempotent behavior (trust galleria's internal change detection)
  - [ ] `site deploy` - Bunny CDN upload (calls build if needed)
- [ ] Each command checks if work already done and skips unnecessary operations

#### 2.3: Configuration Architecture (Separate Configs)

**TDD Implementation Plan** - Replace ad-hoc config loading with unified architecture

**Outer Cycle: E2E Integration Test (Initially Skipped)**
- [ ] E2E test: Complete config integration workflow (`test/e2e/test_config_integration.py`)
  - [ ] Test all commands (validate, organize, build) load configs correctly
  - [ ] Test config validation across site, normpic, pelican, galleria modules
  - [ ] Test missing config file scenarios with meaningful error messages
  - [ ] Test invalid config content scenarios with schema validation
  - [ ] Test config file corruption and JSON parsing errors
  - [ ] **Mark with `@pytest.mark.skip` initially - drives inner cycles**

**Inner Cycle 1: Serializer Module (RED → GREEN → REFACTOR)**
- [ ] Unit test: JSON config loader with schema validation (`test/unit/serializer/test_json_loader.py`)
  - [ ] Test JSON loading with valid configs
  - [ ] Test error handling for malformed JSON files
  - [ ] Test schema validation failures with specific error messages
  - [ ] Test config file not found scenarios
  - [ ] **Should fail initially (RED phase)**
- [ ] Research: Verify normpic's JSON schema format and requirements
  - [ ] Check normpic.Config class structure and expected fields
  - [ ] Document normpic config requirements for schema design
- [ ] Implementation: Core config serializer (`serializer/json.py`)
  - [ ] JSON config loader with schema validation support
  - [ ] Comprehensive error handling with meaningful messages
  - [ ] Support for schema-based validation with jsonschema library
  - [ ] **Make unit tests pass (GREEN phase)**

**Inner Cycle 2: Schema System (RED → GREEN → REFACTOR)** ✅ COMPLETED
- [x] Unit test: Config schema validation (`test/unit/config/test_schemas.py`)
  - [x] Test each config schema validates correct configs
  - [x] Test schema rejection of invalid configs with specific errors
  - [x] Test schema validation for required vs optional fields
  - [x] Test schema validation for field types and formats
  - [x] **Should fail initially (RED phase)**
- [x] Research: Verify galleria's existing config schema in this project
  - [x] Check galleria/config.py structure and requirements
  - [x] Document galleria config requirements for schema design
- [x] Implementation: JSON schema files and validation (`config/schema/`)
  - [x] `site.json` schema - Orchestration, output paths, CDN deployment
  - [x] `normpic.json` schema - Photo organization settings (based on research)
  - [x] `pelican.json` schema - Site generation (theme, content, URLs)
  - [x] `galleria.json` schema - Gallery generation (based on existing config)
  - [x] Schema validation integration with serializer module
  - [x] **Make unit tests pass (GREEN phase)**

**Inner Cycle 3: Command Integration (RED → GREEN → REFACTOR)** ✅ COMPLETED  
- [x] Unit tests: Update existing command tests to use new config system
  - [x] Update `test/unit/validator/test_config.py` for schema validation
  - [x] Add config validation tests to ConfigValidator unit tests  
  - [x] **Should fail initially as commands don't use new system (RED phase)**
- [x] Implementation: Update ConfigValidator to use unified config system
  - [x] Update `validator/config.py` to use JsonConfigLoader with schemas
  - [x] Replace file existence checks with content validation
  - [x] Ensure backward compatibility when schemas missing
  - [x] **Make validator tests pass (GREEN phase)**
- [x] Implementation: Update build command to use unified config system
  - [x] Update `cli/commands/build.py` to load site.json and galleria.json
  - [x] Replace hard-coded paths with config-driven orchestration
  - [x] Integrate with galleria CLI using proper config files

**Final Integration and Documentation** 🚧 BROKEN - NEEDS MAJOR FIXES
- [x] Unskip E2E test: Verify complete config workflow integration
  - [x] Remove `@pytest.mark.skip` from E2E config integration test
  - [x] Run E2E test to validate complete config system workflow
  - [x] Fix any remaining integration issues discovered by E2E test
- [ ] **CRITICAL: Fix build command galleria integration breakage**
  - [ ] Build command replaced subprocess calls with direct imports but broke everything
  - [ ] All 9 unit tests in `test/unit/cli/test_build.py` are skipped (broken mocks)
  - [ ] E2E test `test_build_uses_galleria_module_not_subprocess` is skipped (Pelican errors)
  - [ ] Build command now fails with real usage due to Pelican configuration issues
  - [ ] **Fix Pelican integration issues:**
    - [ ] Update pelican.json schema with all required Pelican settings (THEME, IGNORE_FILES, DELETE_OUTPUT_DIRECTORY, etc.)
    - [ ] Use `pelican.settings.configure_settings()` instead of manual dict construction
    - [ ] Create proper content directory structure in temp filesystem for tests
    - [ ] Handle theme validation - either use default theme or create theme directory
    - [ ] Research complete list of Pelican required settings through documentation or source code
  - [ ] **Fix galleria integration pattern:**
    - [ ] Current direct import approach works but implementation is incomplete
    - [ ] Pipeline stages and plugin registration are correct
    - [ ] Config mapping from galleria.json to plugin config needs validation
  - [ ] **Rewrite unit tests for new architecture:**
    - [ ] Mock `PipelineManager`, `configure_settings`, plugin classes instead of old `galleria` module
    - [ ] Update all test assertions to match new direct import call patterns
    - [ ] Fix config loader mocking to match JsonConfigLoader usage pattern
  - [ ] Need to complete E2E test to actually verify the integration works
- [ ] Production config files: Create actual config files for wedding site
  - [ ] `config/site.json` - Production orchestration settings
  - [ ] `config/normpic.json` - Wedding photo organization settings
  - [ ] `config/pelican.json` - Site generation configuration
  - [ ] `config/galleria.json` - Wedding gallery configuration
- [x] Documentation updates (before each commit):
  - [x] Update `doc/TODO.md` with completed items (mark with [x])
  - [x] Update `doc/CHANGELOG.md` with implementation details and dates
  - [x] Create `doc/configuration.md` - Config system usage guide
  - [x] Create `doc/modules/serializer.md` - Serializer module documentation
  - [x] Update `doc/architecture.md` with config architecture details
  - [x] Update `doc/workflow.md` with config file examples and usage

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

- [ ] **Serve Command Implementation (Post-MVP)**
  - [ ] Plan `site serve` command for development workflow
    - [ ] E2E test: Development server with hot reload (`test/e2e/test_site_serve.py`)
    - [ ] Unit tests: File watching, server management (`test/unit/serve/`)
    - [ ] Inner cycles: Static file server, change detection, rebuild triggers
    - [ ] Implementation: `cli/commands/serve.py` with build integration
    - [ ] Documentation: Serve command usage, development workflow
    - [ ] Commit intervals: test → implementation → integration → docs

- [x] **E2E test performance optimization** 
  - [x] Fix 16+ second subprocess startup time in E2E tests (unacceptable)
  - [x] Replace subprocess calls with direct function calls in E2E tests
  - [x] Consolidate 4 separate E2E tests into single comprehensive workflow test
  - [x] Achieve 460x performance improvement: 37s → 0.08s for organize E2E tests
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
