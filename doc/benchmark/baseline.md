# Wedding Gallery Baseline Performance

Baseline metrics collected 2026-01-13 before any optimization work.

## Configuration

| Setting | Value |
|---------|-------|
| Photos | 645 |
| Photos per page | 96 |
| Thumbnail size | 400px |
| Quality | 85 |
| Pages generated | 8 |

## Lighthouse Scores

| Category | Score |
|----------|-------|
| Performance | 76 |
| Accessibility | 91 |
| Best Practices | 92 |
| SEO | 83 |

## Core Web Vitals

| Metric | Value | Assessment |
|--------|-------|------------|
| FCP | 1,206 ms | Good |
| LCP | 1,880 ms | Good |
| CLS | 0.667 | Poor |
| TBT | 0 ms | Excellent |
| Speed Index | 1,206 ms | Good |

## Build Pipeline Timing

| Stage | Duration |
|-------|----------|
| validate | 0.41s |
| organize | 0.41s |
| build | 410.65s |
| **Total** | **411.47s** |

Build processes 645 photos in ~6.9 minutes (0.64s per photo average).

## Output Sizes

| Asset | Size |
|-------|------|
| Thumbnails (645) | 18.25 MB |
| HTML (8 pages) | 189.8 KB |
| CSS | 2.8 KB |
| **Per thumbnail avg** | **29.7 KB** |
| **Per HTML page avg** | **23.7 KB** |

## Key Observations

### Strengths

- **Zero blocking time** - No JavaScript means TBT of 0ms
- **Fast initial paint** - FCP and LCP both under 2 seconds
- **High accessibility** - 91 score with minimal effort
- **Small CSS footprint** - Under 3KB total

### Areas for Improvement

- **CLS of 0.667 is poor** - Images likely causing layout shift as they load. Need explicit width/height attributes or aspect-ratio CSS.
- **Build time is slow** - 6.9 minutes for full build. Thumbnail generation dominates. Parallel processing could help.
- **Large thumbnail payload** - First page loads 96 thumbnails (~2.9 MB). Lazy loading would improve initial load.

## Optimization Priorities

Based on this baseline:

1. **Fix CLS** - Add image dimensions to prevent layout shift (biggest UX win)
2. **Add lazy loading** - Defer off-screen thumbnail loading
3. **Parallelize thumbnail generation** - Reduce build time
4. **Consider thumbnail compression** - 29.7 KB average may have room for reduction

## Data File

Full metrics: [results/2026-01-13_baseline.json](results/2026-01-13_baseline.json)
