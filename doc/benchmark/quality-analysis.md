# WebP Quality Analysis

Analysis of WebP thumbnail quality settings and parallel processing performance.

## Test Configuration

| Setting | Value |
|---------|-------|
| Test dataset | Wedding gallery (645 photos) |
| Source resolution | 5472x3648 (Canon R5 RAW exports) |
| Thumbnail size | 400x400 px |
| Test machine | [CPU model, cores] |

## Quality Comparison

Testing quality settings 60, 70, 80, 90 on representative sample of 645 photos.

### Metrics Summary

| Quality | Avg File Size | Total Size | Encode Time | Visual Assessment |
|---------|---------------|------------|-------------|-------------------|
| 60 | [X] KB | [X] MB | [X]s | [Notes] |
| 70 | [X] KB | [X] MB | [X]s | [Notes] |
| 80 | [X] KB | [X] MB | [X]s | [Notes] |
| 90 | [X] KB | [X] MB | [X]s | [Notes] |

### Sample Photos

Visual comparison at each quality level for 3 representative photos:

1. **High detail** (foliage, texture)
   - [Link to external comparison image]

2. **Faces/portraits** (skin tone, detail)
   - [Link to external comparison image]

3. **High contrast** (shadows, highlights)
   - [Link to external comparison image]

### File Size Distribution

| Quality | Min | P25 | Median | P75 | Max |
|---------|-----|-----|--------|-----|-----|
| 60 | [X] KB | [X] KB | [X] KB | [X] KB | [X] KB |
| 70 | [X] KB | [X] KB | [X] KB | [X] KB | [X] KB |
| 80 | [X] KB | [X] KB | [X] KB | [X] KB | [X] KB |
| 90 | [X] KB | [X] KB | [X] KB | [X] KB | [X] KB |

## Parallel Processing Performance

Sequential baseline compared against parallel processing with varying worker counts.

### Sequential Baseline

| Metric | Value |
|--------|-------|
| Total photos | 645 |
| Total time | [X]s |
| Avg per photo | [X]ms |
| Photos/second | [X] |

### Scaling Results

| Workers | Total Time | Speedup | Efficiency | Photos/sec |
|---------|------------|---------|------------|------------|
| 1 (seq) | [X]s | 1.0x | 100% | [X] |
| 2 | [X]s | [X]x | [X]% | [X] |
| 4 | [X]s | [X]x | [X]% | [X] |
| 8 | [X]s | [X]x | [X]% | [X] |
| 16 | [X]s | [X]x | [X]% | [X] |

**Efficiency** = (Speedup / Workers) * 100%

### Observations

- [Note about parallel scaling behavior]
- [Note about CPU utilization]
- [Note about diminishing returns threshold]

## Recommendations

### Quality Setting

**Recommended: Quality [X]**

Justification:
- [File size vs visual quality tradeoff]
- [Impact on page load performance]
- [Comparison to baseline quality=85]

### Parallel Workers

**Recommended: [X] workers**

Justification:
- [Efficiency vs speedup tradeoff]
- [Based on typical build server specs]
- [Diminishing returns analysis]

## Running Benchmarks

To reproduce these measurements:

```bash
# Sequential baseline with benchmark metrics
uv run site build --galleria-only --config processor.benchmark=true

# Parallel processing with specific worker count
uv run site build --galleria-only --config processor.parallel=true --config processor.max_workers=4 --config processor.benchmark=true
```

## Data Files

- Sequential baseline: [results/YYYY-MM-DD_sequential.json](results/)
- Parallel results: [results/YYYY-MM-DD_parallel.json](results/)
