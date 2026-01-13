# Performance Benchmarking

## Overview

This directory contains performance metrics, analysis, and documentation for the site build pipeline and frontend UX.

**Goal**: Collect hard numbers to guide post-MVP optimization priorities.

## Metric Categories

### UX/Frontend Metrics (Browser-side)

- **Core Web Vitals**: LCP (Largest Contentful Paint), FID/INP (Interaction to Next Paint), CLS (Cumulative Layout Shift)
- **Loading Timeline**: TTFB (Time to First Byte), FCP (First Contentful Paint), TTI (Time to Interactive)
- **Page Weight**: Total HTML size, CSS size, thumbnail payload per page
- **Lighthouse Scores**: Performance, Accessibility, Best Practices

### Build/Generation Metrics (Pipeline-side)

- **Pipeline Stage Timing**: validate, organize, build durations
- **Thumbnail Processing**: Time per photo, batch throughput, output file sizes
- **Gallery Generation**: Time per collection, total build time, memory usage
- **Output Sizes**: HTML per page, total CSS, manifest sizes

## Collection Methodology

### UX Metrics: Lighthouse CLI

```bash
# Install (one-time)
npm install -g lighthouse

# Start local server
uv run site serve --no-generate

# Run Lighthouse against local server (in another terminal)
CHROME_PATH=/usr/bin/chromium lighthouse http://localhost:8000/galleries/wedding/ \
  --output=json --output-path=./.benchmarks/lighthouse.json \
  --chrome-flags="--headless --no-sandbox"

# Run with HTML report
CHROME_PATH=/usr/bin/chromium lighthouse http://localhost:8000/galleries/wedding/ \
  --output=html --output-path=./.benchmarks/report.html \
  --chrome-flags="--headless --no-sandbox"
```

### Build Metrics: Automated

```bash
# Full pipeline with benchmarking (recommended)
uv run site benchmark

# Individual command with benchmark flag
uv run site validate --benchmark
uv run site organize --benchmark
uv run site build --benchmark
```

Output goes to `/.benchmarks/` (gitignored).

### Build Metrics: Manual Timing

```bash
# Time individual stages manually
time uv run site validate
time uv run site organize
time uv run site build
```

## Directory Structure

```
doc/benchmark/
├── README.md              # This file - methodology and overview
├── baseline.md            # Wedding gallery baseline analysis
├── pagination.md          # Photos-per-page comparison analysis
└── results/               # Curated, annotated results (committed)
    └── baseline-wedding.json
```

```
/.benchmarks/              # Raw output (gitignored)
└── *.json                 # Temporary benchmark results
```

## Workflow

1. Run benchmarks (Lighthouse or `site benchmark`)
2. Review raw results in `/.benchmarks/`
3. Annotate meaningful results with metadata
4. Copy curated results to `doc/benchmark/results/`
5. Write analysis in markdown files

## Result File Format

```json
{
  "metadata": {
    "date": "2025-01-12T14:30:00Z",
    "commit": "f3ad92a",
    "description": "Baseline measurement of wedding gallery",
    "config": {
      "photos_per_page": 100,
      "photo_count": 645,
      "collection": "wedding"
    },
    "notes": "Pre-optimization baseline, default settings"
  },
  "ux_metrics": {
    "lcp_ms": 2400,
    "fcp_ms": 1200,
    "tti_ms": 3500,
    "cls": 0.05,
    "performance_score": 85,
    "accessibility_score": 92,
    "best_practices_score": 100
  },
  "build_metrics": {
    "validate_duration_s": 0.5,
    "organize_duration_s": 16,
    "build_duration_s": 364,
    "thumbnail_count": 645,
    "thumbnail_total_size_mb": 45.2
  }
}
```

**Automated fields**: `date`, `commit`, `build_metrics` (all timing and sizes)

**Manual fields**: `description` (customized), `config`, `notes`, `ux_metrics`

## Analysis Documents

- [baseline.md](baseline.md) - Wedding gallery baseline metrics and observations
- [pagination.md](pagination.md) - Photos-per-page comparison (20, 50, 100, 150, 200, 300, 500)

## Related Documentation

- [TODO.md](../TODO.md) - Phase 7 benchmarking tasks
- [workflow.md](../workflow.md) - Pipeline stage documentation
