# Galleria Architecture

## Design Principles

### Functional Module Organization
- No generic "core" directories
- Modules organized by specific function
- Clear responsibility boundaries
- Each module does one thing well

### Manifest-Driven
- Input: NormPic JSON manifests
- Output: Static HTML galleries
- No database or state management
- Configuration determines behavior

## Module Structure
```
galleria/
\u251c\u2500\u2500 generator/      # Orchestration
\u251c\u2500\u2500 processor/      # Image processing  
\u251c\u2500\u2500 renderer/       # Output generation
\u251c\u2500\u2500 reader/         # Input parsing
\u251c\u2500\u2500 theme/          # Theming system
\u2514\u2500\u2500 plugin/         # Plugin system
```

## Module Responsibilities

### generator/
Orchestrates the gallery generation workflow:
- Loads configuration
- Coordinates other modules
- Handles errors
- Reports progress

### processor/
Handles all image operations:
- Thumbnail generation
- Format conversion
- Optimization
- Caching

### renderer/
Generates output files:
- HTML pages
- CSS stylesheets
- Asset copying
- Directory structure

### reader/
Parses input data:
- NormPic manifest loading
- JSON validation
- Data structure creation

### theme/
Manages visual presentation:
- Template loading
- Theme configuration
- Asset bundling

### plugin/
Extends functionality:
- Plugin loading
- Hook management
- Feature extensions

## Data Flow
```
Config \u2192 Generator \u2192 Reader \u2192 Manifest Data
                       \u2193
                   Processor \u2192 Thumbnails
                       \u2193
                   Renderer \u2192 HTML/CSS
                       \u2193
                   Output Directory
```

## Key Interfaces

### Configuration
```python
{
    "manifest_path": str,
    "output_dir": str,
    "thumbnail_size": int,
    "photos_per_page": int,
    "theme": str
}
```

### Manifest Data
```python
{
    "collection_name": str,
    "pics": List[Dict],
    "generated_at": str
}
```

### Photo Data
```python
{
    "source_path": str,
    "dest_path": str,
    "timestamp": str,
    "camera": str
}
```

## Extension Points

### Themes
- Custom HTML templates
- CSS variations
- JavaScript enhancements

### Plugins
- Pre-processing hooks
- Post-processing hooks
- Custom renderers

## Future Considerations

### Performance
- Parallel processing
- Incremental generation
- Caching strategies

### Features
- Mirror set support
- Multiple size variants
- Video support