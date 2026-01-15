"""Configuration loading and validation for Galleria CLI."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click


@dataclass
class PipelineStageConfig:
    """Configuration for a single pipeline stage."""

    plugin: str
    config: dict[str, Any]


@dataclass
class PipelineConfig:
    """Configuration for the entire plugin pipeline."""

    provider: PipelineStageConfig
    processor: PipelineStageConfig
    transform: PipelineStageConfig
    template: PipelineStageConfig
    css: PipelineStageConfig


@dataclass
class GalleriaConfig:
    """Complete Galleria configuration."""

    input_manifest_path: Path
    output_directory: Path
    pipeline: PipelineConfig

    @classmethod
    def from_file(
        cls, config_path: Path, output_override: Path | None = None
    ) -> "GalleriaConfig":
        """Load and validate configuration from JSON file."""
        if not config_path.exists():
            raise click.FileError(str(config_path), hint="Configuration file not found")

        try:
            with open(config_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(
                f"Invalid JSON in configuration file: {e}"
            ) from e

        # Parse flat config format
        try:
            manifest_path = Path(data["manifest_path"])
        except KeyError as e:
            raise click.ClickException("Missing required field: manifest_path") from e

        # Parse output configuration (allow CLI override)
        if output_override:
            output_dir = output_override
        else:
            try:
                output_dir = Path(data["output_dir"])
            except KeyError as e:
                raise click.ClickException("Missing required field: output_dir") from e

        # Create default pipeline configuration with settings from flat config
        pipeline_stages = {
            "provider": PipelineStageConfig(plugin="normpic-provider", config={}),
            "processor": PipelineStageConfig(
                plugin="thumbnail-processor",
                config={
                    "thumbnail_size": data.get("thumbnail_size", 400),
                    "quality": data.get("quality", 90),
                    # Only include parallel options if specified in config
                    **({"parallel": data["parallel"]} if "parallel" in data else {}),
                    **({"max_workers": data["max_workers"]} if "max_workers" in data else {}),
                },
            ),
            "transform": PipelineStageConfig(
                plugin="basic-pagination",
                config={"page_size": data.get("page_size", 20)},
            ),
            "template": PipelineStageConfig(
                plugin="basic-template",
                config={
                    "theme": data.get("theme", "minimal"),
                    "layout": data.get("layout", "grid"),
                },
            ),
            "css": PipelineStageConfig(
                plugin="basic-css",
                config={
                    "theme": "light"  # CSS plugin only accepts "light", "dark", "auto"
                },
            ),
        }

        pipeline = PipelineConfig(
            provider=pipeline_stages["provider"],
            processor=pipeline_stages["processor"],
            transform=pipeline_stages["transform"],
            template=pipeline_stages["template"],
            css=pipeline_stages["css"],
        )

        return cls(
            input_manifest_path=manifest_path,
            output_directory=output_dir,
            pipeline=pipeline,
        )

    def validate_paths(self) -> None:
        """Validate that required paths exist."""
        if not self.input_manifest_path.exists():
            raise click.ClickException(
                f"Manifest file not found: {self.input_manifest_path}"
            )

        # Output directory doesn't need to exist (will be created)

    def to_pipeline_config(self) -> dict[str, dict[str, Any]]:
        """Convert to pipeline manager configuration format."""
        return {
            "provider": self.pipeline.provider.config,
            "processor": self.pipeline.processor.config,
            "transform": self.pipeline.transform.config,
            "template": self.pipeline.template.config,
            "css": self.pipeline.css.config,
        }
