"""GalleriaBuilder for extracting galleria generation logic."""

from pathlib import Path

from galleria.manager.pipeline import PipelineManager
from galleria.plugins.base import PluginContext
from galleria.plugins.css import BasicCSSPlugin
from galleria.plugins.pagination import BasicPaginationPlugin
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins.template import BasicTemplatePlugin
from .exceptions import GalleriaError


class GalleriaBuilder:
    """Handles galleria pipeline setup and execution."""

    def __init__(self):
        """Initialize GalleriaBuilder."""
        pass

    def build(self, galleria_config: dict, base_dir: Path) -> bool:
        """Build galleria using the pipeline.
        
        Args:
            galleria_config: Galleria configuration dict
            base_dir: Base directory for resolving paths
            
        Returns:
            True if successful
            
        Raises:
            GalleriaError: If generation fails
        """
        try:
            # Resolve paths relative to base_dir
            manifest_path = base_dir / galleria_config["manifest_path"]
            output_dir = base_dir / galleria_config["output_dir"]
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize pipeline and register plugins
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
                error_msg = "Pipeline execution failed: " + ", ".join(final_result.errors)
                raise GalleriaError(error_msg)
            
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
            
            return True
            
        except Exception as e:
            raise GalleriaError(f"Galleria generation failed: {e}") from e