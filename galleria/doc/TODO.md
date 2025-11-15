# Galleria - TODO

## MVP Implementation

### Core Functionality
- [ ] Set up module structure
  - [ ] Create generator/ directory
  - [ ] Create processor/ directory
  - [ ] Create renderer/ directory
  - [ ] Create reader/ directory
- [ ] Implement manifest reader
  - [ ] Parse NormPic JSON manifest
  - [ ] Validate manifest structure
  - [ ] Extract photo metadata
- [ ] Implement thumbnail processor
  - [ ] Load original images from source paths
  - [ ] Generate 400x400 square thumbnails
  - [ ] Convert to WebP format
  - [ ] Save to output directory
- [ ] Implement HTML renderer
  - [ ] Generate paginated HTML (60 photos/page)
  - [ ] Create thumbnail grid layout
  - [ ] Add navigation links (Previous/Next)
  - [ ] Link thumbnails to full-size images
- [ ] Implement CSS renderer
  - [ ] Create base gallery styles
  - [ ] Use CSS Grid for layout
  - [ ] Ensure responsive design
  - [ ] Generate per-gallery CSS file
- [ ] Implement gallery generator
  - [ ] Orchestrate all components
  - [ ] Handle configuration
  - [ ] Create output directory structure
  - [ ] Report progress/errors

### CLI Interface
- [ ] Create __main__.py entry point
- [ ] Implement --config flag
- [ ] Add --verbose flag
- [ ] Add --dry-run flag
- [ ] Handle errors gracefully

### Testing
- [ ] Set up pytest structure
- [ ] Test manifest reader
- [ ] Test thumbnail processor
- [ ] Test HTML generation
- [ ] Test CSS generation
- [ ] Integration tests

### Documentation
- [ ] Document configuration format
- [ ] Create architecture guide
- [ ] Write usage examples
- [ ] Document theme structure

## Post-MVP Features

### Customization
- [ ] Configurable thumbnail sizes
- [ ] Aspect ratio preservation option
- [ ] Multiple thumbnail quality settings
- [ ] Configurable photos per page

### Theme System
- [ ] Extract theme to separate module
- [ ] Create theme base class
- [ ] Implement theme inheritance
- [ ] Add dark mode theme variant

### Plugin System
- [ ] Design plugin interface
- [ ] Implement plugin loading
- [ ] Create example plugins
  - [ ] EXIF display
  - [ ] Photo download options
  - [ ] Social sharing

### Performance
- [ ] Parallel thumbnail processing
- [ ] Incremental generation (skip unchanged)
- [ ] Memory-efficient processing for large collections
- [ ] WebP compression optimization

### Output Options
- [ ] JSON data export for JS frameworks
- [ ] RSS feed generation
- [ ] Sitemap generation
- [ ] Open Graph meta tags

### Mirror Set Support
- [ ] Handle photographer web-optimized versions
- [ ] Fill gaps with auto-generated versions
- [ ] Size variant selection UI

## Technical Debt
- [ ] Add type hints throughout
- [ ] Improve error messages
- [ ] Add logging system
- [ ] Create development mode

## Future Considerations
- [ ] Video support
- [ ] RAW file processing
- [ ] Cloud storage integration
- [ ] GUI for configuration