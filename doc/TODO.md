# Marco & Chrissy's Website - TODO

## Task Management via TODO

### Workflow

Tasks in this file follow the systematic planning approach defined in [`PLANNING.md`](PLANNING.md). This ensures consistent, high-quality development that naturally follows the workflow rules in [`CONTRIBUTE.md`](CONTRIBUTE.md).

**Key principle**: Following TODO tasks should automatically result in following our development workflow.

For detailed planning guidance, templates, and examples, see: **[`PLANNING.md`](PLANNING.md)**

## MVP Roadmap

### Phase 6: Deploy Command & Guided Real-World Deployment

#### Task 6.1: Deploy Command Implementation (Branch: ft/deploy)

*Problem Statement: Site lacks deployment capability to bunny.net CDN. Need dual storage zone strategy (photos vs site content), manifest-based incremental uploads, and integration with existing 4-stage pipeline (validate→organize→build→deploy).*

**Phase 1: Setup & E2E Definition**
- [x] `git checkout -b ft/deploy`
- [x] Create E2E test in `test/e2e/test_site_deploy.py`
  - [x] Test Click deploy function directly (no subprocess)
  - [x] Mock all bunny.net API calls with proper fixtures and isolation
  - [x] Verify dual zone routing: photos→photo zone, site content→site zone
  - [x] Test manifest comparison determines incremental uploads
  - [x] Test pipeline integration: deploy auto-calls build if needed
  - [x] Add `@pytest.mark.skip("Deploy command not implemented")`
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Tst: Add E2E test for deploy command (skipped)`

**Phase 2: TDD Implementation Cycles**

*Cycle 1: Bunny.net API Client Foundation*
- [x] Create stub `deploy/bunnynet_client.py` with `BunnyNetClient` class
- [x] Write unit test for authentication validation (NEVER read/inspect env vars)
- [x] Implement basic auth using BUNNYNET_STORAGE_PASSWORD env var
- [x] Write unit test for file upload with proper headers that fails
- [x] Implement file upload using requests PUT
- [x] Write unit test for manifest download that fails  
- [x] Implement file download for manifest retrieval
- [x] Write unit test for HTTP error handling that fails
- [x] Add comprehensive error handling for API failures
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Ft: Add BunnyNet API client with upload/download`

*Cycle 2: Deployment Manifest Comparison Logic*

**Architecture Decision:** Deploy uses deployment manifests (simple file→hash mapping) separate from normpic manifests (rich photo metadata). This supports dual-zone strategy: photos (output/pics/full/) → photo zone, site content (output/ excluding pics/) → site zone.

- [ ] Create stub `deploy/manifest_comparator.py` with comparison functions  
- [ ] Write unit test for file hash calculation that fails
- [ ] Implement SHA-256 file hashing with chunked reading
- [ ] Write unit test for local manifest generation that fails
- [ ] Implement directory scanning (exclude manifest.json files)
- [ ] Write unit test for manifest comparison logic that fails
- [ ] Implement manifest diff logic (new/changed files detection)
- [ ] Write unit test for JSON serialization that fails
- [ ] Implement manifest JSON load/save functions
- [ ] Write unit test for missing remote manifest handling that fails
- [ ] Handle missing/corrupted remote manifest edge cases
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md  
- [ ] Commit: `Ft: Add deployment manifest comparison for incremental uploads`

*Cycle 3: Deploy Orchestrator & Zone Routing*
- [ ] Create stub `deploy/orchestrator.py` with `DeployOrchestrator` class
- [ ] Write unit test for file routing logic that fails
- [ ] Implement photo zone routing (/output/pics/* → photo zone)
- [ ] Write unit test for photo deployment that fails
- [ ] Implement full photo upload (manifest-based) + thumbnail upload (always)
- [ ] Write unit test for site content deployment that fails
- [ ] Implement site content zone deployment (everything except pics/)
- [ ] Write unit test for partial failure rollback that fails
- [ ] Add rollback logic on deployment failures
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add deploy orchestrator with dual zone strategy`

*Cycle 4: CLI Command Integration*
- [ ] Create stub `cli/commands/deploy.py` following existing command patterns
- [ ] Write unit test for argument parsing that fails
- [ ] Implement deploy command CLI interface
- [ ] Write unit test for orchestrator integration that fails
- [ ] Connect CLI to deploy orchestrator
- [ ] Write unit test for pipeline cascading that fails
- [ ] Implement auto-call to build command (cascading pattern)
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add deploy CLI command with pipeline integration`

**Phase 3A: Critical Implementation Fixes (TDD Cycles)**

*Problem Statement: Four blocking issues prevent bunny.net deployment functionality, discovered during real-world testing with 697 site files. These must be resolved before Phase 3 guided testing can proceed.*

*TDD Cycle 1: Fix Orchestrator API Method Signatures*
- [x] Write unit test for correct `upload_file()` calls with 3 arguments (zone_name parameter)
- [x] Run test - should fail due to current 2-argument calls
- [x] Update `DeployOrchestrator.__init__()` to accept photo/site zone names  
- [x] Fix `deploy_photos():84,92` to call `upload_file(local_path, remote_path, photo_zone_name)`
- [x] Fix `deploy_site_content():119` to call `upload_file(local_path, remote_path, site_zone_name)`
- [x] Run test - should pass
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [x] Update TODO.md and CHANGELOG.md
- [x] Commit: `Fix: Add zone_name parameter to orchestrator upload_file calls`

*TDD Cycle 2: Fix Zone Name Typo and CLI Integration*
- [x] Write unit test expecting correct zone name format (isolated test values)
- [x] Fix hardcoded "marco-chrissy-site" → "marco-crissy-site" throughout documentation
- [x] Update environment variable references in documentation
- [x] Write unit test for CLI reading zone names from environment variables
- [x] Fix deploy CLI command to read zone names from env vars and pass to orchestrator
- [x] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Fix: Add zone name env var support to deploy CLI command`

*TDD Cycle 3: Implement Dual Client Architecture*
- [ ] Write unit tests for zone-specific client creation
- [ ] Update orchestrator to accept separate photo/site clients
- [ ] Update client factory to support dual password configuration
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Ft: Add dual client architecture for zone-specific passwords`

*TDD Cycle 4: Verify ManifestComparator Import*
- [ ] Write integration test importing ManifestComparator in orchestrator context
- [ ] Verify import works (file exists at `deploy/manifest_comparator.py`)
- [ ] If needed, fix import paths or missing dependencies
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit any fixes with: `Fix: Resolve ManifestComparator import issues`

**Phase 3: Interactive Bunny.net Setup & Documentation** *(BLOCKED until Phase 3A complete)*
- [x] Guide user through photo storage zone creation → COMPLETED: zone `marco-crissy-site-pics` 
- [x] Guide user through site storage zone creation → COMPLETED: zone `marco-crissy-site`
- [x] Guide user through finding storage passwords → DISCOVERED: Each zone has unique password
- [x] **CRITICAL: Fix deploy config architecture** - implement flat config with env var names
- [x] **CRITICAL: Fix BunnyNetClient instantiation** - currently missing required password parameter
- [x] Test basic API connectivity with updated config approach
- [ ] Document dual-zone setup with config-driven env vars in `doc/bunnynet.md` - NEEDS UPDATE after blocking fixes
- [ ] Remove `@pytest.mark.skip` from E2E test 
- [ ] Verify E2E test passes (if not, return to Phase 2)
- [ ] Update `doc/README.md` to link to `doc/bunnynet.md`
- [ ] Update `doc/commands/deploy.md` with usage examples
- [ ] Update `doc/bunnynet.md` with correct zone names, dual client architecture, and remove temporary workarounds

**DISCOVERED ISSUES FROM INTERACTIVE SETUP:**
- [ ] **Test filesystem pollution**: Tests writing to `PROJECT_ROOT/output/galleries` instead of isolated temp dirs
- [x] **Config architecture**: Need flat config approach with configurable env var names for dual passwords
- [x] **Dual password reality**: Each storage zone requires separate password (not shared)
- [x] **Deploy client creation**: `BunnyNetClient()` called without required password parameter

**Real-world Setup Results:**
- Photo Zone: `marco-crissy-site-pics` (Frankfurt)
- Site Zone: `marco-crissy-site` (Stockholm + NY replication) 
- Password Env Vars: `BUNNYNET_PASS_MC_PICS`, `BUNNYNET_PASS_MC_SITE`

**BLOCKING ISSUES DISCOVERED DURING REAL-WORLD TESTING:**
- **API Method Signature Mismatch**: Orchestrator calls `upload_file(str(relative_path), file_content)` with 2 arguments, but BunnyNet client expects `upload_file(local_path, remote_path, zone_name)` with 3 arguments
- **Zone Name Typo**: Code references "marco-chrissy-site" but actual zone is "marco-crissy-site" (missing 'h')
- **Single Client Architecture**: Current code uses single `BUNNYNET_STORAGE_PASSWORD`, but real deployment needs zone-specific passwords
- **Missing ManifestComparator**: Orchestrator tries to instantiate `ManifestComparator` but module doesn't exist

**Phase 4: Integration Testing & PR Creation**
- [ ] Test complete validate→organize→build→deploy pipeline end-to-end
- [ ] Verify dual zone deployment works correctly
- [ ] Verify incremental upload behavior (manifest comparison)
- [ ] Test error handling and rollback scenarios
- [ ] `uv run ruff check --fix --unsafe-fixes && uv run pytest`
- [ ] Update TODO.md and CHANGELOG.md
- [ ] Commit: `Tst: Verify complete deploy pipeline integration`
- [ ] `gh pr create --title "Ft: Implement bunny.net deploy command" --body "Adds deploy command with dual storage zone strategy, manifest-based incremental uploads, and integration with existing build pipeline"`

**Environment Variables Required:**
- `BUNNYNET_STORAGE_PASSWORD` - Storage zone password (NEVER inspect/print)
- `BUNNYNET_PHOTO_ZONE_NAME` - Photo storage zone name
- `BUNNYNET_SITE_ZONE_NAME` - Site content storage zone name  
- `BUNNYNET_REGION` - Storage region (optional, defaults to Frankfurt)

**Success Criteria:**
- [ ] Wedding gallery deploys successfully to bunny.net
- [ ] Incremental uploads work (only changed files uploaded)
- [ ] Dual zone strategy separates photos from site content
- [ ] Deploy integrates seamlessly with existing pipeline
- [ ] Documentation guides user through complete setup

### Phase 7: Performance Baseline

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
