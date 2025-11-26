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
    def from_file(cls, config_path: Path, output_override: Path | None = None) -> 'GalleriaConfig':
        """Load and validate configuration from JSON file."""
        if not config_path.exists():
            raise click.FileError(str(config_path), hint="Configuration file not found")

        try:
            with open(config_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON in configuration file: {e}") from e

        # Validate required top-level structure
        try:
            input_config = data["input"]
            output_config = data["output"]
            pipeline_config = data["pipeline"]
        except KeyError as e:
            raise click.ClickException(f"Missing required configuration section: {e}") from e

        # Parse input configuration
        try:
            manifest_path = Path(input_config["manifest_path"])
        except KeyError as e:
            raise click.ClickException("Missing required field: input.manifest_path") from e

        # Parse output configuration (allow CLI override)
        if output_override:
            output_dir = output_override
        else:
            try:
                output_dir = Path(output_config["directory"])
            except KeyError as e:
                raise click.ClickException("Missing required field: output.directory") from e

        # Parse pipeline configuration
        try:
            pipeline_stages = {}
            required_stages = ["provider", "processor", "transform", "template", "css"]

            for stage in required_stages:
                if stage not in pipeline_config:
                    raise click.ClickException(f"Missing required pipeline stage: {stage}")

                stage_config = pipeline_config[stage]

                # Validate stage structure
                if "plugin" not in stage_config:
                    raise click.ClickException(f"Missing plugin name for stage: {stage}")

                plugin_name = stage_config["plugin"]
                stage_specific_config = stage_config.get("config", {})

                pipeline_stages[stage] = PipelineStageConfig(
                    plugin=plugin_name,
                    config=stage_specific_config
                )

            pipeline = PipelineConfig(
                provider=pipeline_stages["provider"],
                processor=pipeline_stages["processor"],
                transform=pipeline_stages["transform"],
                template=pipeline_stages["template"],
                css=pipeline_stages["css"]
            )

        except Exception as e:
            if isinstance(e, click.ClickException):
                raise
            raise click.ClickException(f"Invalid pipeline configuration: {e}") from e

        return cls(
            input_manifest_path=manifest_path,
            output_directory=output_dir,
            pipeline=pipeline
        )

    def validate_paths(self) -> None:
        """Validate that required paths exist."""
        if not self.input_manifest_path.exists():
            raise click.ClickException(f"Manifest file not found: {self.input_manifest_path}")

        # Output directory doesn't need to exist (will be created)

    def to_pipeline_config(self) -> dict[str, dict[str, Any]]:
        """Convert to pipeline manager configuration format."""
        return {
            "provider": self.pipeline.provider.config,
            "processor": self.pipeline.processor.config,
            "transform": self.pipeline.transform.config,
            "template": self.pipeline.template.config,
            "css": self.pipeline.css.config
        }
