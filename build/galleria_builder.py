"""GalleriaBuilder for extracting galleria generation logic."""

from pathlib import Path
from typing import Optional

from galleria.manager.pipeline import PipelineManager
from galleria.plugins.base import PluginContext
from galleria.plugins.css import BasicCSSPlugin
from galleria.plugins.pagination import BasicPaginationPlugin
from galleria.plugins.processors.thumbnail import ThumbnailProcessorPlugin
from galleria.plugins.providers.normpic import NormPicProviderPlugin
from galleria.plugins.template import BasicTemplatePlugin
from .context import BuildContext
from .exceptions import GalleriaError


class GalleriaBuilder:
    """Handles galleria pipeline setup and execution."""

    def __init__(self):
        """Initialize GalleriaBuilder."""
        pass

    def _get_theme_path(self, theme_name: str) -> str:
        """Get the filesystem path to a Galleria theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Absolute path to theme directory
        """
        from pathlib import Path
        # Assuming themes are in galleria/themes/ relative to this file
        galleria_root = Path(__file__).parent.parent / "galleria"
        theme_path = galleria_root / "themes" / theme_name
        return str(theme_path)

    def build(
        self, 
        galleria_config: dict, 
        base_dir: Path, 
        build_context: Optional[BuildContext] = None,
        site_url: Optional[str] = None
    ) -> bool:
        """Build galleria using the pipeline.
        
        Args:
            galleria_config: Galleria configuration dict
            base_dir: Base directory for resolving paths
            build_context: BuildContext for production vs development mode
            site_url: Base URL for the site (when using build_context)
            
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
            
            # Create metadata with BuildContext if provided
            metadata = {}
            if build_context is not None and site_url is not None:
                metadata["build_context"] = build_context
                metadata["site_url"] = site_url

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
                        "title": "Gallery",
                        "theme_path": self._get_theme_path(galleria_config.get("theme", "minimal")),
                        "shared_theme_path": str(base_dir / galleria_config["SHARED_THEME_PATH"]) if galleria_config.get("SHARED_THEME_PATH") else None
                    },
                    "css": {
                        "shared_theme_path": str(base_dir / galleria_config["SHARED_THEME_PATH"]) if galleria_config.get("SHARED_THEME_PATH") else None
                    }
                },
                output_dir=output_dir,
                metadata=metadata
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