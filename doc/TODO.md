# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development

#### Core Functionality
- [ ] Set up Galleria module structure
  - [ ] Create generator/ directory
  - [ ] Create processor/ directory
  - [ ] Create template/ directory
  - [ ] Create serializer/ directory
  - [ ] Create themes/ directory
- [ ] Implement serializer module
  - [ ] Parse NormPic JSON manifest
  - [ ] Load and validate galleria configuration
  - [ ] Handle schema validation for configs and manifests
- [ ] Implement thumbnail processor
  - [ ] Load original images from source paths
  - [ ] Generate 400x400 square thumbnails
  - [ ] Convert to WebP format
  - [ ] Save to output directory
- [ ] Implement template module
  - [ ] Load HTML templates from themes
  - [ ] Generate paginated HTML (60 photos/page)
  - [ ] Create thumbnail grid layout
  - [ ] Add navigation links (Previous/Next)
  - [ ] Link thumbnails to full-size images
  - [ ] Generate CSS stylesheets
  - [ ] Support plugin template injection
- [ ] Design plugin interface (foundational)
  - [ ] Define plugin hook points
  - [ ] Create plugin base class/interface
  - [ ] Design plugin discovery mechanism
  - [ ] Document plugin architecture
- [ ] Implement gallery generator
  - [ ] Orchestrate all components
  - [ ] Handle configuration
  - [ ] Create output directory structure
  - [ ] Report progress/errors
  - [ ] Integrate plugin hook points

#### CLI Interface
- [ ] Create __main__.py entry point
- [ ] Implement --config flag
- [ ] Add --verbose flag
- [ ] Add --dry-run flag
- [ ] Handle errors gracefully

#### Testing & Validation
- [ ] Set up pytest structure for Galleria
- [ ] Test manifest reader
- [ ] Test thumbnail processor
- [ ] Test HTML generation
- [ ] Test CSS generation
- [ ] Integration tests
- [ ] Test Galleria with wedding photo collection

#### Documentation
- [ ] Document Galleria configuration format
- [ ] Update Galleria architecture guide
- [ ] Write Galleria usage examples
- [ ] Document theme structure

### Phase 2: Site Structure
- [ ] Set up site project module structure
  - [ ] Create build/ directory
  - [ ] Create validation/ directory
  - [ ] Create deployment/ directory
  - [ ] Create configuration/ directory
- [ ] Implement command system
  - [ ] Create cascading command structure (validate → organize → build → deploy)
  - [ ] Implement validate command
  - [ ] Implement organize command (orchestrate NormPic)
  - [ ] Implement build command (orchestrate Galleria + Pelican)
  - [ ] Implement deploy command (orchestrate CDN upload)
- [ ] Set up Pelican configuration
  - [ ] Basic theme selection
  - [ ] Configure output paths
  - [ ] Set up URL structure
- [ ] Create content pages
  - [ ] Gallery index page (/galleries/)
  - [ ] About us page (/about/)
- [ ] Create configuration files
  - [ ] Site orchestration config
  - [ ] NormPic config for wedding collection
  - [ ] Galleria config for wedding gallery

### Phase 3: Integration Testing
- [ ] Test command system end-to-end
- [ ] Validate site generation workflow
- [ ] Test Galleria + Pelican integration

### Phase 4: Performance Baseline
- [ ] Measure initial performance metrics
  - [ ] Page weight (HTML + CSS + thumbnails)
  - [ ] Core Web Vitals (FCP, LCP, TTI, CLS, TBT)
  - [ ] Lighthouse scores
- [ ] Document baseline metrics
- [ ] Create performance tracking spreadsheet

## Post-MVP Enhancements

### Near-term Optimizations
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
  - [ ] Add comprehensive type hints
  - [ ] Improve error messages and logging
  - [ ] Create development/debug mode
  - [ ] Performance optimization and profiling

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
1. \u2705 Wedding gallery is live on Bunny CDN
2. \u2705 Gallery index and about pages are live
3. \u2705 Site works without JavaScript
4. \u2705 Performance metrics are documented
5. \u2705 Build process is repeatable via script

## Notes

- Maintain non-JS functionality as primary requirement
- All enhancements must use progressive enhancement
- Performance metrics before and after each optimization
- Keep Galleria extractable for future open-sourcing
- Design plugin interface from day one - modularity is foundational
- Plugin hooks should be lightweight and clearly defined
- Each component should be pluggable without tight coupling