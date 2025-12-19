"""Template loading for Galleria theme system."""

from pathlib import Path

import jinja2


class TemplateLoader:
    """Loads and renders Jinja2 templates from theme directories."""

    def __init__(self, theme_path: str, theme_template_overrides: str = None):
        """Initialize template loader with theme path.

        Args:
            theme_path: Path to theme directory
            theme_template_overrides: Optional path to shared theme directory
        """
        self.theme_path = Path(theme_path)
        self.templates_dir = self.theme_path / "templates"
        self.shared_templates_dir = Path(theme_template_overrides) / "templates" if theme_template_overrides else None

    def load_template(self, template_name: str) -> jinja2.Template:
        """Load Jinja2 template from theme directory.

        Args:
            template_name: Name of template file to load

        Returns:
            Loaded Jinja2 template

        Raises:
            TemplateNotFoundError: If template file doesn't exist
        """
        # Build list of template search paths (theme first, then shared)
        search_paths = [str(self.templates_dir)]
        if self.shared_templates_dir and self.shared_templates_dir.exists():
            search_paths.append(str(self.shared_templates_dir))

        # Create Jinja2 environment with theme and shared template directories
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(search_paths),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Load and return template
        return env.get_template(template_name)
