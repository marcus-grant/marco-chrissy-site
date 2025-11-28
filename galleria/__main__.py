"""Galleria CLI entry point."""

from pathlib import Path

import click

from .config import GalleriaConfig
from .manager.pipeline import PipelineManager
from .plugins.base import PluginContext
from .plugins.css import BasicCSSPlugin
from .plugins.pagination import BasicPaginationPlugin
from .plugins.processors.thumbnail import ThumbnailProcessorPlugin
from .plugins.providers.normpic import NormPicProviderPlugin
from .plugins.template import BasicTemplatePlugin


@click.group()
@click.version_option(version="0.1.0", prog_name="galleria")
def cli():
    """Galleria static gallery generator."""
    pass


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to galleria configuration file"
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated gallery (overrides config)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
def generate(config: Path, output: Path | None, verbose: bool):
    """Generate static gallery from configuration file.

    This command processes a photo collection through the galleria plugin
    pipeline to generate a static HTML gallery with thumbnails.
    """
    if verbose:
        click.echo(f"Loading configuration from: {config}")
        if output:
            click.echo(f"Output directory override: {output}")

    # Load and validate configuration
    try:
        galleria_config = GalleriaConfig.from_file(config, output)
        galleria_config.validate_paths()
    except click.ClickException:
        raise  # Re-raise click exceptions as-is
    except Exception as e:
        raise click.ClickException(f"Configuration error: {e}") from e

    if verbose:
        click.echo(f"Manifest path: {galleria_config.input_manifest_path}")
        click.echo(f"Output directory: {galleria_config.output_directory}")
        click.echo("Configuration loaded and validated successfully")

    # Create output directory
    galleria_config.output_directory.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline manager and register plugins
    if verbose:
        click.echo("Initializing plugin pipeline...")

    pipeline = PipelineManager()
    pipeline.registry.register(NormPicProviderPlugin(), "provider")
    pipeline.registry.register(ThumbnailProcessorPlugin(), "processor")
    pipeline.registry.register(BasicPaginationPlugin(), "transform")
    pipeline.registry.register(BasicTemplatePlugin(), "template")
    pipeline.registry.register(BasicCSSPlugin(), "css")

    # Define pipeline stages
    stages = [
        ("provider", "normpic-provider"),
        ("processor", "thumbnail-processor"),
        ("transform", "basic-pagination"),
        ("template", "basic-template"),
        ("css", "basic-css")
    ]

    # Create initial context
    initial_context = PluginContext(
        input_data={"manifest_path": str(galleria_config.input_manifest_path)},
        config=galleria_config.to_pipeline_config(),
        output_dir=galleria_config.output_directory
    )

    # Execute pipeline with progress reporting
    if verbose:
        click.echo("Executing plugin pipeline:")

    try:
        for i, (stage, plugin_name) in enumerate(stages, 1):
            if verbose:
                click.echo(f"  [{i}/{len(stages)}] Running {stage} ({plugin_name})...")

        # Execute complete pipeline
        final_result = pipeline.execute_stages(stages, initial_context)

        if not final_result.success:
            error_msg = "Pipeline execution failed:\n" + "\n".join(final_result.errors)
            raise click.ClickException(error_msg)

        if verbose:
            click.echo("Pipeline execution completed successfully")

        # Write generated files to disk
        final_output = final_result.output_data
        collection_name = final_output.get("collection_name", "gallery")

        # Write HTML files
        if "html_files" in final_output:
            for html_file in final_output["html_files"]:
                html_path = galleria_config.output_directory / html_file["filename"]
                html_path.write_text(html_file["content"], encoding="utf-8")
                if verbose:
                    click.echo(f"  Wrote: {html_path}")

            page_count = len(final_output["html_files"])
            click.echo(f"Generated {page_count} HTML pages for '{collection_name}'")

        # Write CSS files
        if "css_files" in final_output:
            for css_file in final_output["css_files"]:
                css_path = galleria_config.output_directory / css_file["filename"]
                css_path.write_text(css_file["content"], encoding="utf-8")
                if verbose:
                    click.echo(f"  Wrote: {css_path}")

            css_count = len(final_output["css_files"])
            click.echo(f"Generated {css_count} CSS files")

        if "thumbnail_count" in final_output:
            thumb_count = final_output["thumbnail_count"]
            click.echo(f"Processed {thumb_count} thumbnails")

        click.echo(f"Gallery generated successfully in: {galleria_config.output_directory}")

    except Exception as e:
        if isinstance(e, click.ClickException):
            raise
        raise click.ClickException(f"Pipeline execution error: {e}") from e




def main():
    """Entry point for the galleria CLI."""
    cli()


if __name__ == "__main__":
    main()

