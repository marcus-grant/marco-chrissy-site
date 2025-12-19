# Architecture Decision Notes

## Static Site Generator Evaluation (Dec 2025)

### Current State: Python + Pelican
- **Working**: Shared components, gallery integration, build pipeline
- **Frustrations**: Web 1.0 assumptions, automatic title generation, `<hgroup>` elements
- **Workarounds**: Template overrides to fight default behaviors

### Pelican vs 11ty Trade-offs

**11ty Advantages:**
- Modern HTML5 approach, zero assumptions about markup
- Clean template composition vs file replacement overrides
- Better JavaScript integration for progressive enhancement
- No fighting framework defaults for clean semantic HTML

**Python Ecosystem Advantages:**
- **Deployment flexibility**: FaaS everywhere, preinstalled on Linux hosts
- **HTMX synergy**: Same backend code works static OR dynamic
- **Microservices**: FastAPI/Flask for simple, well-scoped services
- **Existing toolchain**: NormPic, Galleria, photo processing pipeline

## Strategic Direction

### Short Term: Current Project (Marco+Chrissy Site)
- **Decision**: Keep Python/Pelican, publish and improve UX
- **Rationale**: Template overrides solved main issues, avoid scope creep
- **Focus**: Documentation, performance, deployment

### Personal Site Architecture Experiment
- **Goal**: Test 11ty + Python hybrid approach
- **Content**: Markdown-based, POSSE features, personal photos
- **Integration**: 11ty consumes Galleria JSON output
- **Learning**: Evaluate JS vs Python for future decisions

### HTMX Personal Notes Wiki
- **Implementation**: Python microservice (FastAPI)
- **Deployment**: Subdomain, simple nginx proxy
- **Features**: Wiki-style content, personalized note-taking
- **Strategy**: Prove HTMX + Python backend patterns

## Key Decision Factors for Future Sites

### Deployment Strategy Priority
- **Requirement**: Single codebase → static, FaaS, VPS, containers
- **Python advantage**: Better deployment flexibility, fewer dependencies
- **Node consideration**: Version management complexity, ecosystem lock-in

### HTMX Integration
- **Python ecosystem**: Mature HTML-first templating (Jinja2)  
- **Node ecosystem**: JSON-first assumptions, fewer HTMX patterns
- **Decision driver**: Progressive enhancement over SPA complexity

### Component Modularity
- **Extract**: NormPic, Galleria, shared components, build patterns
- **Test**: Personal site as proving ground for modular architecture
- **Goal**: Reusable components across multiple deployment strategies

## Data-Oriented Static Site Generation

### 11ty's Pipeline Philosophy
- **Templates as data transformers**: Each template step processes and transforms data
- **Clean separation**: Content → data → templates → output
- **Composable**: Pipeline stages can be reordered, extended, or replaced
- **Debuggable**: Each step produces inspectable intermediate data

### Potential Custom Implementation (Python)
**Core concept**: Static site generator focused on data flow over file conventions

**Pipeline stages:**
1. **Content ingestion**: Markdown, JSON, API calls → normalized data structures
2. **Data transformation**: Filters, aggregation, cross-references → enriched data  
3. **Template rendering**: Jinja2/similar → HTML fragments
4. **Asset processing**: CSS, images, static files → optimized outputs
5. **Site assembly**: Combine fragments → complete pages

**Python advantages for data-oriented approach:**
- **Rich data ecosystem**: pandas, pydantic for structured data processing
- **Template flexibility**: Jinja2 already proven in this project
- **Pipeline libraries**: Click, dask for complex data flows
- **Extensibility**: Plugin system using Python imports/decorators

### Alternative Static Site Generators to Evaluate

**Sphinx** (Python):
- Very flexible, designed for complex documentation
- Strong cross-referencing and data relationship features
- May be overkill but worth investigating for data-heavy sites

**Zola** (Rust):
- Single binary, very fast
- Data-oriented approach with taxonomies and sections
- Limited ecosystem but clean design

**Hugo** (Go):
- Extremely fast, good data processing features
- Template system supports complex data manipulation
- Large ecosystem but opinionated about structure

**Astro** (JavaScript):
- Component-based, excellent JavaScript integration
- Islands architecture for selective hydration
- Good for mixed static/dynamic content

### Custom Implementation Considerations

**Benefits:**
- **Perfect fit**: Designed exactly for your data flow needs
- **No framework fighting**: Zero unwanted opinions or legacy baggage
- **Python ecosystem**: Leverage existing photo processing, HTMX backend
- **Learning value**: Deep understanding of static site generation principles

**Implementation approach:**
```python
# Conceptual pipeline
content_data = ingest_content(markdown_files, json_data, api_sources)
enriched_data = transform_data(content_data, cross_references, metadata)
rendered_fragments = render_templates(enriched_data, template_system)
optimized_assets = process_assets(css_files, images, static_content)
final_site = assemble_site(rendered_fragments, optimized_assets)
```

**Key design principles:**
- **Data first**: Everything is data transformation
- **Immutable stages**: Each pipeline step produces new data, never modifies input
- **Plugin architecture**: Each stage configurable/replaceable
- **CLI + library**: Usable as command-line tool or imported module

**Complexity considerations:**
- **Time investment**: Significant upfront development vs using existing tools
- **Maintenance burden**: Long-term support and feature development
- **Ecosystem**: Would need to build plugin/theme ecosystem from scratch

## Open Questions

1. **Template system**: Is fighting Pelican worth the Python ecosystem benefits?
2. **JavaScript enhancement**: How much interactivity before complexity outweighs benefits?
3. **POSSE integration**: Best patterns for social media syndication?
4. **Photo processing**: Can Galleria work seamlessly with 11ty data consumption?
5. **Custom implementation**: Is the learning/control value worth the development time?
6. **Data complexity**: How much data processing do static sites actually need?

## Next Steps

1. Complete current project documentation and deployment
2. Extract core components (Galleria, shared themes) for reusability  
3. Build personal site with 11ty + Python hybrid to test integration patterns
4. Evaluate long-term architecture decisions based on real-world usage