"""Benchmark data structures for performance measurement."""

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable


@dataclass
class BenchmarkMetadata:
    """Metadata for a benchmark result."""

    date: datetime
    commit: str
    description: str
    config: dict[str, Any] | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {
            "date": self.date.isoformat(),
            "commit": self.commit,
            "description": self.description,
        }
        if self.config is not None:
            result["config"] = self.config
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass
class BuildMetrics:
    """Build pipeline performance metrics."""

    validate_duration_s: float | None = None
    organize_duration_s: float | None = None
    build_duration_s: float | None = None
    thumbnail_count: int | None = None
    thumbnail_total_bytes: int | None = None
    html_total_bytes: int | None = None
    css_total_bytes: int | None = None
    html_page_count: int | None = None

    @property
    def total_pipeline_s(self) -> float:
        """Calculate total pipeline duration from component durations."""
        total = 0.0
        if self.validate_duration_s is not None:
            total += self.validate_duration_s
        if self.organize_duration_s is not None:
            total += self.organize_duration_s
        if self.build_duration_s is not None:
            total += self.build_duration_s
        return total

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {}
        if self.validate_duration_s is not None:
            result["validate_duration_s"] = self.validate_duration_s
        if self.organize_duration_s is not None:
            result["organize_duration_s"] = self.organize_duration_s
        if self.build_duration_s is not None:
            result["build_duration_s"] = self.build_duration_s
        if self.thumbnail_count is not None:
            result["thumbnail_count"] = self.thumbnail_count
        if self.thumbnail_total_bytes is not None:
            result["thumbnail_total_bytes"] = self.thumbnail_total_bytes
        if self.html_total_bytes is not None:
            result["html_total_bytes"] = self.html_total_bytes
        if self.css_total_bytes is not None:
            result["css_total_bytes"] = self.css_total_bytes
        if self.html_page_count is not None:
            result["html_page_count"] = self.html_page_count
        # Always include calculated total
        result["total_pipeline_s"] = self.total_pipeline_s
        return result


@dataclass
class UXMetrics:
    """UX/Frontend performance metrics from Lighthouse."""

    performance_score: int | None = None
    accessibility_score: int | None = None
    best_practices_score: int | None = None
    seo_score: int | None = None
    fcp_ms: int | None = None
    lcp_ms: int | None = None
    cls: float | None = None
    tbt_ms: int | None = None
    speed_index_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {}
        for field_name in [
            "performance_score",
            "accessibility_score",
            "best_practices_score",
            "seo_score",
            "fcp_ms",
            "lcp_ms",
            "cls",
            "tbt_ms",
            "speed_index_ms",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result


@dataclass
class BenchmarkResult:
    """Complete benchmark result with metadata and metrics."""

    metadata: BenchmarkMetadata
    build_metrics: BuildMetrics | None = None
    ux_metrics: UXMetrics | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {"metadata": self.metadata.to_dict()}
        if self.build_metrics is not None:
            result["build_metrics"] = self.build_metrics.to_dict()
        if self.ux_metrics is not None:
            result["ux_metrics"] = self.ux_metrics.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class TimingContext:
    """Context manager for timing code execution.

    Usage as context manager:
        with TimingContext() as timer:
            # code to time
        print(f"Took {timer.duration_s} seconds")

    Usage as decorator:
        @TimingContext.wrap()
        def my_function():
            pass
        result, timing = my_function()
    """

    def __init__(self, track_memory: bool = False):
        """Initialize TimingContext.

        Args:
            track_memory: Whether to track memory usage (requires tracemalloc)
        """
        self.track_memory = track_memory
        self.duration_s: float | None = None
        self.memory_bytes: int | None = None
        self._start_time: float | None = None
        self._start_memory: int | None = None

    def __enter__(self) -> "TimingContext":
        """Start timing."""
        if self.track_memory:
            import tracemalloc

            tracemalloc.start()
            self._start_memory = tracemalloc.get_traced_memory()[0]

        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timing and record results."""
        if self._start_time is not None:
            self.duration_s = time.perf_counter() - self._start_time

        if self.track_memory:
            import tracemalloc

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if self._start_memory is not None:
                self.memory_bytes = current - self._start_memory
            else:
                self.memory_bytes = current

    @classmethod
    def wrap(
        cls, track_memory: bool = False
    ) -> Callable[[Callable], Callable[..., tuple[Any, "TimingContext"]]]:
        """Create a decorator that times function execution.

        Args:
            track_memory: Whether to track memory usage

        Returns:
            Decorator that returns (result, TimingContext) tuple
        """

        def decorator(func: Callable) -> Callable[..., tuple[Any, "TimingContext"]]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> tuple[Any, "TimingContext"]:
                timer = cls(track_memory=track_memory)
                with timer:
                    result = func(*args, **kwargs)
                return result, timer

            return wrapper

        return decorator
