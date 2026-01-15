"""Benchmark data structures for galleria performance measurement.

This module is kept separate for future galleria extraction.
Follows patterns from build/benchmark.py but is galleria-specific.
"""

from dataclasses import dataclass, field


@dataclass
class ThumbnailBenchmark:
    """Collects per-photo timing and size metrics during thumbnail processing.

    Usage:
        benchmark = ThumbnailBenchmark()
        for photo in photos:
            start = time.perf_counter()
            # ... process photo ...
            duration = time.perf_counter() - start
            size = output_path.stat().st_size
            benchmark.record_photo(duration, size)

        metrics = benchmark.get_metrics()
    """

    per_photo_times: list[float] = field(default_factory=list)
    output_sizes: list[int] = field(default_factory=list)
    total_duration_s: float = 0.0

    def record_photo(self, duration_s: float, output_bytes: int) -> None:
        """Record timing and size for a processed photo.

        Args:
            duration_s: Time taken to process this photo in seconds
            output_bytes: Size of the output thumbnail in bytes
        """
        self.per_photo_times.append(duration_s)
        self.output_sizes.append(output_bytes)
        self.total_duration_s += duration_s

    def get_metrics(self) -> dict:
        """Get all collected metrics as a dictionary.

        Returns:
            Dict containing:
                - per_photo_times: List of per-photo processing times
                - total_duration_s: Sum of all processing times
                - photos_per_second: Throughput (photos / total_duration)
                - output_sizes: List of output file sizes in bytes
                - total_output_bytes: Sum of all output sizes
                - average_output_bytes: Mean output size
        """
        count = len(self.per_photo_times)
        total_bytes = sum(self.output_sizes)

        return {
            "per_photo_times": self.per_photo_times,
            "total_duration_s": self.total_duration_s,
            "photos_per_second": (
                count / self.total_duration_s if self.total_duration_s > 0 else 0.0
            ),
            "output_sizes": self.output_sizes,
            "total_output_bytes": total_bytes,
            "average_output_bytes": total_bytes // count if count > 0 else 0,
        }
