# Marco & Chrissy's Website - TODO

## MVP Roadmap

### Phase 1: Galleria Development
- [ ] Create Galleria MVP implementation
  - [ ] Manifest reader for NormPic output
  - [ ] Thumbnail processor (400x400 square, WebP)
  - [ ] HTML generator with pagination (60 pics/page)
  - [ ] CSS generator (per-gallery stylesheets)
  - [ ] Asset copying (CSS/fonts)
- [ ] Test Galleria with wedding photo collection
- [ ] Document Galleria usage

### Phase 2: Site Structure
- [ ] Set up Pelican configuration
  - [ ] Basic theme selection
  - [ ] Configure output paths
  - [ ] Set up URL structure
- [ ] Create content pages
  - [ ] Gallery index page (/galleries/)
  - [ ] About us page (/about/)
- [ ] Integrate Galleria output with Pelican

### Phase 3: Orchestration
- [ ] Create build.py script
  - [ ] Run NormPic for photo organization
  - [ ] Run Galleria for gallery generation
  - [ ] Run Pelican for site generation
  - [ ] Validate output structure
- [ ] Create configuration files
  - [ ] Site orchestration config
  - [ ] NormPic config for wedding collection
  - [ ] Galleria config for wedding gallery

### Phase 4: Deployment
- [ ] Create deploy.py script
  - [ ] Upload to Bunny CDN site bucket
  - [ ] Set appropriate cache headers
  - [ ] Validate deployment
- [ ] Configure Bunny CDN
  - [ ] Set up DNS records
  - [ ] Configure pull zones
  - [ ] Set cache policies

### Phase 5: Performance Baseline
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
- [ ] Add Christmas gallery
- [ ] Add vacation gallery

### Medium-term Features
- [ ] Photographer web-optimized mirror set handling
- [ ] Multiple photo size options for download
- [ ] Gallery search/filter capabilities
- [ ] Blog/updates section
- [ ] Christmas card pages

### Infrastructure Improvements
- [ ] GitHub Actions CI/CD pipeline
- [ ] Docker containerization consideration
- [ ] Ansible automation evaluation
- [ ] CDN optimization (separate bucket strategies)

### Long-term Considerations
- [ ] Django integration for dynamic features
- [ ] CMS integration (Wagtail evaluation)
- [ ] API endpoints for gallery data
- [ ] Mobile app considerations

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