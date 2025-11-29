"""Galleria CLI entry point."""

from pathlib import Path

import click

from .config import GalleriaConfig
from .manager.pipeline import PipelineManager
from .orchestrator.serve import ServeOrchestrator
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
        print(f"DEBUG: About to enumerate stages: {stages}")
        for i, (stage, plugin_name) in enumerate(stages, 1):
            print(f"DEBUG: Loop iteration {i}, stage: {stage}, plugin: {plugin_name}")
            if verbose:
                click.echo(f"  [{i}/{len(stages)}] Running {stage} ({plugin_name})...")

        print("DEBUG: About to execute pipeline")
        # Execute complete pipeline
        final_result = pipeline.execute_stages(stages, initial_context)
        print("DEBUG: Pipeline execution completed")

        if not final_result.success:
            error_msg = "Pipeline execution failed:\n" + "\n".join(final_result.errors)
            raise click.ClickException(error_msg)

        if verbose:
            click.echo("Pipeline execution completed successfully")

        # Write generated files to disk
        final_output = final_result.output_data
        collection_name = final_output.get("collection_name", "gallery")

        # TODO: REFACTOR FILE WRITING SYSTEM
        # The current file writing validation is defensive programming against malformed plugin output.
        # This indicates a design problem: plugins should not be able to generate invalid data structures.
        # Post-MVP: Implement proper schema validation at plugin interface level and structured output types.
        # See post-MVP task: "Refactor plugin output validation to use structured types and schema validation"

        # Write HTML files
        if "html_files" in final_output:
            for i, html_file in enumerate(final_output["html_files"]):
                try:
                    # Validate file structure before writing
                    if not isinstance(html_file, dict):
                        raise click.ClickException(f"HTML file {i} is not a dictionary: {type(html_file)}")

                    if "filename" not in html_file:
                        raise click.ClickException(f"HTML file {i} missing required 'filename' field")

                    if "content" not in html_file:
                        raise click.ClickException(f"HTML file {i} missing required 'content' field")

                    content = html_file["content"]
                    if content is None:
                        raise click.ClickException(f"HTML file {i} has None content")

                    if not isinstance(content, str):
                        raise click.ClickException(f"HTML file {i} content is not a string: {type(content)}")

                    # Check content size to prevent massive files
                    if len(content) > 50_000_000:  # 50MB limit
                        raise click.ClickException(f"HTML file {i} content too large: {len(content)} bytes")

                    html_path = galleria_config.output_directory / html_file["filename"]
                    html_path.write_text(content, encoding="utf-8")
                    if verbose:
                        click.echo(f"  Wrote: {html_path}")

                except Exception as e:
                    if isinstance(e, click.ClickException):
                        raise
                    raise click.ClickException(f"Failed to write HTML file {i}: {e}") from e

            page_count = len(final_output["html_files"])
            click.echo(f"Generated {page_count} HTML pages for '{collection_name}'")

        # Write CSS files
        if "css_files" in final_output:
            for i, css_file in enumerate(final_output["css_files"]):
                try:
                    # Validate file structure before writing
                    if not isinstance(css_file, dict):
                        raise click.ClickException(f"CSS file {i} is not a dictionary: {type(css_file)}")

                    if "filename" not in css_file:
                        raise click.ClickException(f"CSS file {i} missing required 'filename' field")

                    if "content" not in css_file:
                        raise click.ClickException(f"CSS file {i} missing required 'content' field")

                    content = css_file["content"]
                    if content is None:
                        raise click.ClickException(f"CSS file {i} has None content")

                    if not isinstance(content, str):
                        raise click.ClickException(f"CSS file {i} content is not a string: {type(content)}")

                    # Check content size to prevent massive files
                    if len(content) > 10_000_000:  # 10MB limit for CSS
                        raise click.ClickException(f"CSS file {i} content too large: {len(content)} bytes")

                    css_path = galleria_config.output_directory / css_file["filename"]
                    css_path.write_text(content, encoding="utf-8")
                    if verbose:
                        click.echo(f"  Wrote: {css_path}")

                except Exception as e:
                    if isinstance(e, click.ClickException):
                        raise
                    raise click.ClickException(f"Failed to write CSS file {i}: {e}") from e

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


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to galleria configuration file"
)
@click.option(
    "--host", "-h",
    default="127.0.0.1",
    help="Host address to bind server (default: 127.0.0.1)"
)
@click.option(
    "--port", "-p",
    type=int,
    default=8000,
    help="Port number for development server (default: 8000)"
)
@click.option(
    "--no-generate",
    is_flag=True,
    help="Skip gallery generation phase"
)
@click.option(
    "--no-watch",
    is_flag=True,
    help="Disable file watching and hot reload"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
def serve(config: Path, host: str, port: int, no_generate: bool, no_watch: bool, verbose: bool):
    """Start development server for gallery with hot reload.

    This command starts an HTTP server to serve the generated gallery files
    with optional file watching for hot reload during development.
    """
    if verbose:
        click.echo("Starting galleria development server...")
        click.echo(f"Configuration: {config}")
        click.echo(f"Server: http://{host}:{port}")
        if no_generate:
            click.echo("Skipping gallery generation")
        if no_watch:
            click.echo("File watching disabled")

    try:
        # Initialize and execute serve orchestrator
        orchestrator = ServeOrchestrator()
        orchestrator.execute(
            config_path=config,
            host=host,
            port=port,
            no_generate=no_generate,
            no_watch=no_watch,
            verbose=verbose
        )
    except KeyboardInterrupt:
        if verbose:
            click.echo("\nShutting down server...")
        click.echo("Development server stopped.")
    except Exception as e:
        raise click.ClickException(f"Server error: {e}") from e




def main():
    """Entry point for the galleria CLI."""
    cli()


if __name__ == "__main__":
    main()

