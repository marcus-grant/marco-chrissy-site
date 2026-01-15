#!/usr/bin/env python3
"""Benchmark WebP quality at a specific level.

Usage:
    uv run python scripts/benchmark_quality.py <manifest_path> <output_dir> <quality>

Example:
    uv run python scripts/benchmark_quality.py output/pics/full/manifest.json .benchmarks/q60 60
"""

import json
import shutil
import sys
import time
from pathlib import Path

from galleria.plugins.base import PluginContext
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin

# Optimal worker count from parallel scaling benchmark (8 cores, 5.25x speedup)
OPTIMAL_WORKERS = 8


def load_manifest(manifest_path: Path) -> dict:
    """Load photos from normpic manifest."""
    with open(manifest_path) as f:
        manifest = json.load(f)

    photos = []
    for pic in manifest.get("pics", []):
        photos.append({
            "source_path": pic["source_path"],
            "dest_path": pic["dest_path"],
            "metadata": {
                "hash": pic.get("hash", ""),
                "size_bytes": pic.get("size_bytes", 0),
                "mtime": pic.get("mtime", 0),
            }
        })

    return {
        "photos": photos,
        "collection_name": manifest.get("collection_name", "benchmark"),
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: uv run python scripts/benchmark_quality.py <manifest_path> <output_dir> <quality>")
        print("Example: uv run python scripts/benchmark_quality.py output/pics/full/manifest.json .benchmarks/q60 60")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    quality = int(sys.argv[3])

    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        sys.exit(1)

    print(f"Loading manifest from {manifest_path}...")
    provider_data = load_manifest(manifest_path)
    num_photos = len(provider_data["photos"])
    print(f"Found {num_photos} photos")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    print(f"\n{'=' * 60}")
    print(f"QUALITY BENCHMARK: q={quality} ({OPTIMAL_WORKERS} workers)")
    print("=" * 60)

    context = PluginContext(
        input_data=provider_data,
        config={
            "thumbnail_size": 400,
            "quality": quality,
            "parallel": True,
            "max_workers": OPTIMAL_WORKERS,
            "benchmark": True,
            "use_cache": False,
        },
        output_dir=output_dir,
    )

    plugin = ThumbnailProcessorPlugin()

    print(f"\nProcessing {num_photos} photos at quality={quality}...")
    start = time.perf_counter()
    result = plugin.process_thumbnails(context)
    total_time = time.perf_counter() - start

    if result.success and "benchmark" in result.output_data:
        bm = result.output_data["benchmark"]

        thumbnails_dir = output_dir / "thumbnails"
        sizes = [f.stat().st_size for f in thumbnails_dir.glob("*.webp")]
        total_size = sum(sizes)
        avg_size = total_size / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)

        # Calculate percentiles
        sorted_sizes = sorted(sizes)
        p25_idx = len(sorted_sizes) // 4
        p50_idx = len(sorted_sizes) // 2
        p75_idx = (3 * len(sorted_sizes)) // 4

        results = {
            "quality": quality,
            "num_photos": num_photos,
            "total_time_s": round(total_time, 2),
            "photos_per_second": round(bm["photos_per_second"], 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "avg_size_kb": round(avg_size / 1024, 1),
            "min_size_kb": round(min_size / 1024, 1),
            "max_size_kb": round(max_size / 1024, 1),
            "p25_size_kb": round(sorted_sizes[p25_idx] / 1024, 1),
            "p50_size_kb": round(sorted_sizes[p50_idx] / 1024, 1),
            "p75_size_kb": round(sorted_sizes[p75_idx] / 1024, 1),
        }

        print(f"\n{'=' * 60}")
        print("RESULTS")
        print("=" * 60)
        print(f"Quality:        {quality}")
        print(f"Photos:         {num_photos}")
        print(f"Total time:     {total_time:.1f}s ({bm['photos_per_second']:.1f} photos/s)")
        print(f"Total size:     {total_size/(1024*1024):.2f} MB")
        print(f"Avg size:       {avg_size/1024:.1f} KB")
        print(f"Size range:     {min_size/1024:.1f} - {max_size/1024:.1f} KB")
        print(f"Percentiles:    P25={sorted_sizes[p25_idx]/1024:.1f} KB, "
              f"P50={sorted_sizes[p50_idx]/1024:.1f} KB, "
              f"P75={sorted_sizes[p75_idx]/1024:.1f} KB")

        # Save results
        results_file = output_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {results_file}")
        print(f"Thumbnails in:  {thumbnails_dir}/")
    else:
        print(f"Error: Processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
