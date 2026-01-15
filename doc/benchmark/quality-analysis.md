# WebP Quality Analysis

Analysis of WebP thumbnail quality settings and parallel processing performance.

## Test Configuration

| Setting | Value |
|---------|-------|
| Test dataset | Wedding gallery (645 photos) |
| Source resolution | 5472x3648 (Canon R5 RAW exports) |
| Thumbnail size | 400x400 px |
| Test machine | AMD Ryzen 7 7840U, 8 cores / 16 threads |
| Test date | 2026-01-15 |

## Quality Comparison

Testing quality settings 50, 60, 70, 80, 90 on 645 photos with 8 parallel workers.

### Metrics Summary

| Quality | Avg Size | Total Size | Encode Time | Subjective Rating |
|---------|----------|------------|-------------|-------------------|
| 50 | 14.6 KB | 9.18 MB | 66.9s | 2.7 |
| 60 | 16.4 KB | 10.34 MB | 60.3s | 3.0 |
| 70 | 18.4 KB | 11.61 MB | 62.1s | 4.0 |
| 80 | 23.7 KB | 14.90 MB | 64.0s | 4.0 |
| 90 | 37.5 KB | 23.64 MB | 67.9s | 4.3 |

### Subjective Quality Assessment

Ratings use a 1-5 Mean Opinion Score (MOS) scale, normalized with q90 as the baseline (best quality = 5 for bouquet sample).

| Score | Label | Meaning |
|-------|-------|---------|
| 5 | Excellent | No visible degradation |
| 4 | Good | Perceptible but not annoying |
| 3 | Fair | Slightly annoying artifacts |
| 2 | Poor | Annoying, noticeable quality loss |
| 1 | Bad | Very annoying, unacceptable |

**Per-sample ratings:**

| Quality | Bouquet | Cathedral | Stage | Average |
|---------|---------|-----------|-------|---------|
| 90 | 5 | 4 | 4 | 4.3 |
| 80 | 4 | 4 | 4 | 4.0 |
| 70 | 4 | 4 | 4 | 4.0 |
| 60 | 3 | 3 | 3 | 3.0 |
| 50 | 2 | 3 | 3 | 2.7 |

**Threshold:** 4.0+ is considered "acceptable quality" for production use.

### Sample Photos

Three photos selected to stress different compression factors:

1. **Cathedral** (`wedding-20250809T161041-r5a.webp`)
   - Tests: Architectural detail + faces + extreme contrast (dim interior vs bright windows)
   - Compression challenge: Fine stonework detail in low light, shadow blocking

2. **Bouquet** (`wedding-20250809T181211-r5a.webp`)
   - Tests: Fine texture (flowers, skin) + jewelry detail + soft gradients
   - Compression challenge: Micro-contrast in petals, color accuracy in skin tones

3. **Stage** (`wedding-20250809T225826-r5a.webp`)
   - Tests: Black backgrounds + colored stage lights + artificial lighting
   - Compression challenge: Color banding in dark areas, posterization, hue shifts

### File Size Distribution

| Quality | Min | P25 | Median | P75 | Max |
|---------|-----|-----|--------|-----|-----|
| 50 | 0.9 KB | 10.2 KB | 13.3 KB | 17.4 KB | 38.8 KB |
| 60 | 1.0 KB | 11.5 KB | 15.1 KB | 19.6 KB | 42.6 KB |
| 70 | 1.1 KB | 12.9 KB | 17.1 KB | 22.0 KB | 47.4 KB |
| 80 | 1.4 KB | 16.8 KB | 22.2 KB | 28.3 KB | 58.4 KB |
| 90 | 2.4 KB | 27.6 KB | 36.1 KB | 44.6 KB | 81.4 KB |

## Parallel Processing Performance

Sequential baseline compared against parallel processing with varying worker counts.

### Sequential Baseline

| Metric | Value |
|--------|-------|
| Total photos | 645 |
| Total time | 359.2s |
| Avg per photo | 557ms |
| Photos/second | 1.8 |

### Scaling Results

| Workers | Total Time | Speedup | Efficiency | Photos/sec |
|---------|------------|---------|------------|------------|
| Sequential | 359.2s | 1.00x | 100% | 1.8 |
| 1 | 364.8s | 0.98x | 98% | 1.8 |
| 2 | 191.7s | 1.87x | 94% | 3.4 |
| 4 | 108.0s | 3.33x | 83% | 6.0 |
| 8 | 68.5s | 5.25x | 66% | 9.4 |
| 16 | 55.7s | 6.45x | 40% | 11.6 |

**Efficiency** = (Speedup / Workers) * 100%

### Observations

- Near-linear scaling up to 4 workers (83% efficiency)
- 8 workers provides best balance: 5.25x speedup with 66% efficiency
- 16 workers shows diminishing returns: only 23% faster than 8 workers but half the efficiency
- Single-worker parallel has ~2% overhead vs sequential due to process pool startup
- Encode time varies only ~8s across quality levels; resize operation dominates

## Recommendations

### Quality Setting

**Recommended: Quality 70**

Justification:
- Same subjective quality as q80 (both score 4.0) but 22% smaller files
- Total gallery size: 11.61 MB vs 14.90 MB at q80, 23.64 MB at q90
- No encode time penalty (all quality levels within 8s of each other)
- Provides 51% file size reduction vs q90 baseline with no perceptible quality loss

### Parallel Workers

**Recommended: 8 workers**

Justification:
- Best efficiency/speedup balance: 5.25x faster at 66% efficiency
- Matches physical core count (8 cores), avoiding hyperthreading contention
- 16 workers only 23% faster but doubles resource usage
- Build time reduced from ~6 minutes to ~1 minute

## Future Work

### Sample Photo Visualization

Sample thumbnails from q50 through q90 for the three test photos (cathedral, bouquet, stage) should be included when publishing this analysis. The samples are archived separately for future reference.

### Comparative Charts

Charts comparing the following dimensions would aid analysis:
- Subjective quality vs file size
- Subjective quality vs encode time
- File size vs encode time

Visualization method TBD. Consider:
- Scatter plots with quality level as point labels
- Multi-axis charts showing all three dimensions
- Side-by-side thumbnail grids at each quality level

## Running Benchmarks

To reproduce these measurements:

```bash
# Parallel scaling benchmark
uv run python scripts/benchmark_parallel.py

# Quality benchmark at specific level
uv run python scripts/benchmark_quality.py output/pics/full/manifest.json .benchmarks/q70 70
```

## Data Files

Archived benchmark data includes:
- `results.json` for each quality level (q50, q60, q70, q80, q90)
- `parallel/results.json` for scaling benchmark
- Sample thumbnails organized by photo type
