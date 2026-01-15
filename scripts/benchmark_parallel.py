#!/usr/bin/env python3
"""Benchmark parallel scaling (sequential, 1, 2, 4, 8, 16 workers).

Usage:
    uv run python scripts/benchmark_parallel.py
"""

import json
import shutil
import time
from pathlib import Path

from galleria.plugins.base import PluginContext
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin


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
    manifest_path = Path("output/pics/full/manifest.json")
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    print(f"Loading manifest from {manifest_path}...")
    provider_data = load_manifest(manifest_path)
    num_photos = len(provider_data["photos"])
    print(f"Found {num_photos} photos")

    output_base = Path(".benchmarks/parallel")
    output_base.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("PARALLEL SCALING BENCHMARK")
    print("=" * 60)

    results = []
    baseline_time = None

    # Sequential baseline
    print("\nRunning sequential baseline...")
    output_dir = output_base / "sequential"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    context = PluginContext(
        input_data=provider_data,
        config={
            "thumbnail_size": 400,
            "quality": 85,
            "parallel": False,
            "benchmark": True,
            "use_cache": False,
        },
        output_dir=output_dir,
    )

    plugin = ThumbnailProcessorPlugin()
    start = time.perf_counter()
    result = plugin.process_thumbnails(context)
    baseline_time = time.perf_counter() - start

    if result.success:
        bm = result.output_data["benchmark"]
        results.append({
            "workers": "seq",
            "time_s": round(baseline_time, 2),
            "speedup": 1.0,
            "efficiency": 100.0,
            "photos_per_second": round(bm["photos_per_second"], 2),
        })
        print(f"  Sequential: {baseline_time:.1f}s ({bm['photos_per_second']:.1f} photos/s)")

    # Parallel with different worker counts
    worker_counts = [1, 2, 4, 8, 16]

    for workers in worker_counts:
        output_dir = output_base / f"workers_{workers}"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)

        context = PluginContext(
            input_data=provider_data,
            config={
                "thumbnail_size": 400,
                "quality": 85,
                "parallel": True,
                "max_workers": workers,
                "benchmark": True,
                "use_cache": False,
            },
            output_dir=output_dir,
        )

        print(f"\nRunning with {workers} worker(s)...")
        start = time.perf_counter()
        result = plugin.process_thumbnails(context)
        total_time = time.perf_counter() - start

        if result.success and "benchmark" in result.output_data:
            bm = result.output_data["benchmark"]
            speedup = baseline_time / total_time if total_time > 0 else 0
            efficiency = (speedup / workers) * 100

            results.append({
                "workers": workers,
                "time_s": round(total_time, 2),
                "speedup": round(speedup, 2),
                "efficiency": round(efficiency, 1),
                "photos_per_second": round(bm["photos_per_second"], 2),
            })

            print(f"  {workers} worker(s): {total_time:.1f}s, {speedup:.2f}x speedup, {efficiency:.0f}% efficiency")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\n{'Workers':<10} {'Time':<10} {'Speedup':<10} {'Efficiency':<12} {'Rate':<12}")
    print("-" * 54)
    for r in results:
        print(f"{r['workers']:<10} {r['time_s']:.1f}s{'':<5} "
              f"{r['speedup']:.2f}x{'':<5} "
              f"{r['efficiency']:.0f}%{'':<7} "
              f"{r['photos_per_second']:.1f}/s")

    # Save results
    results_file = output_base / "results.json"
    with open(results_file, "w") as f:
        json.dump({"parallel_benchmark": results, "num_photos": num_photos, "baseline_time_s": baseline_time}, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
