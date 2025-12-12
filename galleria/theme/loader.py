"""Template loading for Galleria theme system."""

from pathlib import Path

import jinja2


class TemplateLoader:
    """Loads and renders Jinja2 templates from theme directories."""

    def __init__(self, theme_path: str):
        """Initialize template loader with theme path.

        Args:
            theme_path: Path to theme directory
        """
        self.theme_path = Path(theme_path)
        self.templates_dir = self.theme_path / "templates"

    def load_template(self, template_name: str) -> jinja2.Template:
        """Load Jinja2 template from theme directory.

        Args:
            template_name: Name of template file to load

        Returns:
            Loaded Jinja2 template

        Raises:
            TemplateNotFoundError: If template file doesn't exist
        """
        # Create Jinja2 environment with theme templates directory
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Load and return template
        return env.get_template(template_name)
