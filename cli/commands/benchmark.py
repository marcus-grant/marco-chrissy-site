"""Benchmark command implementation."""

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import click

from build.benchmark import (
    BenchmarkMetadata,
    BenchmarkResult,
    BuildMetrics,
    TimingContext,
)


@click.command()
def benchmark():
    """Run full pipeline with benchmark instrumentation.

    Runs validate → organize → build with timing, then outputs
    aggregated results to .benchmarks/ directory.
    """
    click.echo("Running benchmark...")

    # Create .benchmarks directory if it doesn't exist
    benchmarks_dir = Path(".benchmarks")
    benchmarks_dir.mkdir(exist_ok=True)

    # Time each stage
    validate_duration = _time_stage("validate")
    organize_duration = _time_stage("organize")
    build_duration = _time_stage("build")

    # Get current commit hash
    commit = _get_commit_hash()

    # Collect size metrics
    size_metrics = _collect_size_metrics()

    # Create benchmark result
    metadata = BenchmarkMetadata(
        date=datetime.now(UTC),
        commit=commit,
        description="Automated benchmark run",
    )

    build_metrics = BuildMetrics(
        validate_duration_s=validate_duration,
        organize_duration_s=organize_duration,
        build_duration_s=build_duration,
        **size_metrics,
    )

    result = BenchmarkResult(metadata=metadata, build_metrics=build_metrics)

    # Write output file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = benchmarks_dir / f"benchmark_{timestamp}.json"
    output_path.write_text(result.to_json())

    click.echo("✓ Benchmark complete!")
    click.echo(f"  Validate: {validate_duration:.3f}s")
    click.echo(f"  Organize: {organize_duration:.3f}s")
    click.echo(f"  Build: {build_duration:.3f}s")
    click.echo(f"  Total: {build_metrics.total_pipeline_s:.3f}s")
    click.echo(f"  Output: {output_path}")


def _time_stage(stage: str) -> float:
    """Run a pipeline stage and return its duration."""
    click.echo(f"  Running {stage}...")
    with TimingContext() as timer:
        result = subprocess.run(
            ["uv", "run", "site", stage],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"✗ {stage} failed:")
            click.echo(result.stdout)
            click.echo(result.stderr)
            raise click.Abort()

    return timer.duration_s


def _get_commit_hash() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _collect_size_metrics() -> dict:
    """Collect file size metrics from output directory."""
    metrics = {}

    # Thumbnail metrics
    thumbnails_dir = Path("output/galleries/wedding/thumbnails")
    if thumbnails_dir.exists():
        thumbnails = list(thumbnails_dir.glob("*"))
        metrics["thumbnail_count"] = len(thumbnails)
        metrics["thumbnail_total_bytes"] = sum(f.stat().st_size for f in thumbnails)

    # HTML metrics
    galleries_dir = Path("output/galleries/wedding")
    if galleries_dir.exists():
        html_files = list(galleries_dir.glob("*.html"))
        metrics["html_page_count"] = len(html_files)
        metrics["html_total_bytes"] = sum(f.stat().st_size for f in html_files)

        css_files = list(galleries_dir.glob("*.css"))
        metrics["css_total_bytes"] = sum(f.stat().st_size for f in css_files)

    return metrics
