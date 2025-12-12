"""Theme validation for Galleria theme system."""

from pathlib import Path


class ThemeValidator:
    """Validates theme directory structure and required files."""

    def validate_theme_directory(self, theme_path: str) -> dict[str, list]:
        """Validate theme directory structure and required files.

        Args:
            theme_path: Path to theme directory

        Returns:
            Dict with validation results

        Raises:
            ThemeValidationError: If theme structure is invalid
        """
        errors = []
        theme_dir = Path(theme_path)

        # Check theme.json exists
        if not (theme_dir / "theme.json").exists():
            errors.append("theme.json missing")

        # Check template directory and required files
        templates_dir = theme_dir / "templates"
        if not templates_dir.exists():
            errors.append("templates directory missing")
        else:
            required_templates = ["base.j2.html", "gallery.j2.html", "empty.j2.html"]
            for template in required_templates:
                if not (templates_dir / template).exists():
                    errors.append(f"template file missing: {template}")

        # Check static CSS directory
        css_dir = theme_dir / "static" / "css"
        if not css_dir.exists():
            errors.append("static/css directory missing")

        return {"valid": len(errors) == 0, "errors": errors}
