"""Build command implementation."""

import os
from pathlib import Path

import click

import pelican
from serializer.json import JsonConfigLoader
from galleria.config import GalleriaConfig
from galleria.manager.pipeline import PipelineManager
from galleria.plugins.base import PluginContext
from galleria.plugins.css import BasicCSSPlugin
from galleria.plugins.pagination import BasicPaginationPlugin
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins.template import BasicTemplatePlugin

from .organize import organize


@click.command()
def build():
    """Build the complete site with galleries and pages."""
    click.echo("Building site...")

    # Load site configuration
    try:
        config_loader = JsonConfigLoader()
        site_config = config_loader.load_config(Path("config/site.json"))
        galleria_config = config_loader.load_config(Path("config/galleria.json"))
    except Exception as e:
        click.echo(f"✗ Failed to load configuration: {e}")
        ctx = click.get_current_context()
        ctx.exit(1)

    # Run organize first (cascading pattern)
    click.echo("Running organization...")
    ctx = click.get_current_context()
    result = ctx.invoke(organize)

    if result and hasattr(result, 'exit_code') and result.exit_code != 0:
        click.echo("✗ Organize failed - stopping build")
        ctx.exit(1)

    # Check if already built (idempotent behavior)
    output_dir = site_config.get("output_dir", "output")
    if _is_already_built(output_dir):
        click.echo("✓ Site is already built and up to date, skipping...")
        click.echo("Build completed successfully!")
        return

    # Generate galleries using Galleria module directly
    click.echo("Generating galleries with Galleria...")
    try:
        # Create GalleriaConfig from our config data
        manifest_path = Path(galleria_config["manifest_path"])
        output_dir = Path(galleria_config["output_dir"])
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipeline manager and register plugins
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
        
        # Create initial context from galleria config
        initial_context = PluginContext(
            input_data={"manifest_path": str(manifest_path)},
            config={
                "provider": {},
                "processor": {
                    "thumbnail_size": galleria_config.get("thumbnail_size", 400),
                    "quality": galleria_config.get("quality", 85)
                },
                "transform": {
                    "page_size": galleria_config.get("photos_per_page", 60)
                },
                "template": {
                    "theme": galleria_config.get("theme", "minimal"),
                    "title": "Gallery"
                },
                "css": {}
            },
            output_dir=output_dir
        )
        
        # Execute pipeline
        final_result = pipeline.execute_stages(stages, initial_context)
        
        if not final_result.success:
            error_msg = "Galleria pipeline execution failed:\n" + "\n".join(final_result.errors)
            click.echo(f"✗ {error_msg}")
            ctx.exit(1)
            
        # Write generated files to disk
        final_output = final_result.output_data
        
        # Write HTML files
        if "html_files" in final_output:
            for html_file in final_output["html_files"]:
                html_path = output_dir / html_file["filename"]
                html_path.write_text(html_file["content"], encoding="utf-8")
                
        # Write CSS files  
        if "css_files" in final_output:
            for css_file in final_output["css_files"]:
                css_path = output_dir / css_file["filename"]
                css_path.write_text(css_file["content"], encoding="utf-8")
        
        click.echo("✓ Galleria generation completed successfully!")
        
    except Exception as e:
        click.echo(f"✗ Galleria generation failed: {e}")
        ctx.exit(1)

    # Generate site pages using Pelican
    click.echo("Generating site pages with Pelican...")
    try:
        # Load pelican configuration
        pelican_config = config_loader.load_config(Path("config/pelican.json"))
        
        # Use Pelican's default settings and override with our config
        from pelican.settings import configure_settings
        pelican_settings = configure_settings({
            'AUTHOR': pelican_config.get('author', 'Unknown Author'),
            'SITENAME': pelican_config.get('sitename', 'My Site'),  
            'SITEURL': pelican_config.get('site_url', ''),
            'PATH': 'content',
            'OUTPUT_PATH': site_config.get('output_dir', 'output')
        })
        
        pelican_instance = pelican.Pelican(pelican_settings)
        pelican_instance.run()
        click.echo("✓ Pelican generation completed successfully!")
    except Exception as e:
        import traceback
        click.echo(f"✗ Pelican generation failed: {e}")
        click.echo(f"Full traceback: {traceback.format_exc()}")
        ctx.exit(1)

    click.echo("Build completed successfully!")


def _is_already_built(output_dir="output"):
    """Check if site is already built and up to date."""
    # Simple check for key output files existence
    output_paths = [
        f"{output_dir}/galleries",
        f"{output_dir}/index.html"
    ]

    return all(os.path.exists(path) for path in output_paths)
