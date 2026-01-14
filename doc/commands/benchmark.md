# Benchmark Command

## Overview

The benchmark command runs the full pipeline with timing instrumentation, collecting performance metrics for analysis. Results are saved to the `.benchmarks/` directory.

## Usage

```bash
uv run site benchmark
```

## Functionality

The benchmark command:

1. **Times each pipeline stage** - validate, organize, build
2. **Collects size metrics** - thumbnails, HTML pages, CSS files
3. **Records git commit** - Associates metrics with code version
4. **Saves results** - JSON output in `.benchmarks/` directory

## Output

```
Running benchmark...
  Running validate...
  Running organize...
  Running build...
✓ Benchmark complete!
  Validate: 0.234s
  Organize: 2.456s
  Build: 15.789s
  Total: 18.479s
  Output: .benchmarks/benchmark_2026-01-14_143052.json
```

## Metrics Collected

### Timing Metrics
- `validate_duration_s` - Validation phase timing
- `organize_duration_s` - Photo organization timing
- `build_duration_s` - Gallery and site generation timing
- `total_pipeline_s` - Combined pipeline duration

### Size Metrics
- `thumbnail_count` - Number of generated thumbnails
- `thumbnail_total_bytes` - Total thumbnail file size
- `html_page_count` - Number of HTML pages generated
- `html_total_bytes` - Total HTML file size
- `css_total_bytes` - Total CSS file size

### Metadata
- `date` - Benchmark run timestamp (UTC)
- `commit` - Git commit hash (short form)
- `description` - Run description

## Output Format

Results are saved as JSON in `.benchmarks/benchmark_YYYY-MM-DD_HHMMSS.json`:

```json
{
  "metadata": {
    "date": "2026-01-14T14:30:52Z",
    "commit": "abc1234",
    "description": "Automated benchmark run"
  },
  "build_metrics": {
    "validate_duration_s": 0.234,
    "organize_duration_s": 2.456,
    "build_duration_s": 15.789,
    "total_pipeline_s": 18.479,
    "thumbnail_count": 645,
    "thumbnail_total_bytes": 12345678,
    "html_page_count": 33,
    "html_total_bytes": 98765,
    "css_total_bytes": 4567
  }
}
```

## Architecture

The benchmark command uses classes from `build/benchmark.py`:

- **TimingContext** - Context manager for precise timing
- **BenchmarkMetadata** - Run metadata (date, commit, description)
- **BuildMetrics** - Collected timing and size metrics
- **BenchmarkResult** - Combined result with JSON serialization

## Use Cases

### Performance Regression Detection
Compare benchmark results across commits to identify performance regressions.

### Optimization Validation
Run before and after optimization changes to measure improvement.

### CI Integration
Include in CI pipeline to track performance over time.

## Exit Codes

- **0**: Benchmark completed successfully
- **1**: Pipeline stage failed (validate, organize, or build error)

## Troubleshooting

### Stage Failure
If a stage fails, the benchmark aborts and shows the failing stage's output. Fix the underlying issue and re-run.

### Missing Output Directory
The `.benchmarks/` directory is created automatically if it doesn't exist.

### Git Commit Unknown
If not in a git repository, commit shows as "unknown". This doesn't affect other metrics.
