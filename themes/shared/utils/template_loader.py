"""Template loader utilities for shared theme components."""

from pathlib import Path

import jinja2

from defaults import get_shared_template_paths


def configure_pelican_shared_templates(config_path: str) -> list[str]:
    """Configure Pelican Jinja2 environment to include shared template paths.

    Args:
        config_path: Path to Pelican configuration file

    Returns:
        List of template directory paths for Jinja2 loader
    """
    import json

    with open(config_path) as f:
        config = json.load(f)

    template_dirs = []

    # Add shared templates if configured, otherwise use defaults
    if "SHARED_THEME_PATH" in config:
        shared_templates = Path(config["SHARED_THEME_PATH"]) / "templates"
        template_dirs.append(str(shared_templates))
    else:
        # Use default shared template paths
        default_paths = [str(path) for path in get_shared_template_paths()]
        template_dirs.extend(default_paths)

    # Add theme-specific templates
    if "THEME" in config:
        theme_templates = Path(config["THEME"]) / "templates"
        template_dirs.append(str(theme_templates))

    return template_dirs


class GalleriaSharedTemplateLoader:
    """Template loader for Galleria with shared template support."""

    def __init__(self, config: dict, theme_base_path: str):
        """Initialize loader with config and theme path.

        Args:
            config: Galleria configuration dict
            theme_base_path: Base path to specific theme directory (e.g. /path/themes/minimal)
        """
        self.config = config
        self.theme_base_path = Path(theme_base_path)

        # Build template search paths (theme-specific first for precedence)
        search_paths = []

        # 1. Theme-specific templates (highest precedence)
        theme_templates = self.theme_base_path / "templates"
        search_paths.append(str(theme_templates))

        # 2. External/shared templates (lower precedence)
        external_templates = config.get("theme", {}).get("external_templates", [])
        if external_templates:
            search_paths.extend(external_templates)
        else:
            # Use default shared template paths if no external templates configured
            default_paths = [str(path) for path in get_shared_template_paths()]
            search_paths.extend(default_paths)

        # Create Jinja2 environment with search paths
        loader = jinja2.FileSystemLoader(search_paths)
        self.env = jinja2.Environment(loader=loader)

    def get_template(self, template_name: str) -> jinja2.Template:
        """Get template by name from search paths.

        Args:
            template_name: Name of template file (e.g., "navigation.html")

        Returns:
            Jinja2 template object

        Raises:
            TemplateNotFound: If template not found in any search path
        """
        try:
            return self.env.get_template(template_name)
        except jinja2.TemplateNotFound as e:
            raise Exception(f"Template '{template_name}' not found in search paths") from e


def create_example_shared_template(shared_templates_dir: Path) -> Path:
    """Create an example shared template for verification.

    Args:
        shared_templates_dir: Directory to create template in

    Returns:
        Path to created template file
    """
    template_path = shared_templates_dir / "example.html"

    template_content = """<!-- Example shared template -->
<div class="shared-component">
    <h2>Example Shared Component</h2>
    <p>This is an example template that can be included by both Pelican and Galleria.</p>
</div>"""

    template_path.write_text(template_content)
    return template_path
