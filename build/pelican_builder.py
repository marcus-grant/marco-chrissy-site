"""PelicanBuilder for extracting pelican generation logic."""

from pathlib import Path

import pelican
from pelican.settings import DEFAULT_CONFIG, configure_settings
from .exceptions import PelicanError


class PelicanBuilder:
    """Handles pelican site generation."""

    def __init__(self):
        """Initialize PelicanBuilder."""
        pass

    def build(self, site_config: dict, pelican_config: dict, base_dir: Path) -> bool:
        """Build pelican site using configuration.
        
        Args:
            site_config: Site configuration dict
            pelican_config: Pelican configuration dict
            base_dir: Base directory for resolving paths
            
        Returns:
            True if successful
            
        Raises:
            PelicanError: If generation fails
        """
        try:
            # Create content directory if it doesn't exist
            content_path = pelican_config.get('content_path', 'content')
            content_dir = base_dir / content_path
            content_dir.mkdir(parents=True, exist_ok=True)

            # Start with Pelican's full default configuration
            pelican_settings_dict = DEFAULT_CONFIG.copy()

            # Override with our specific settings
            pelican_settings_dict.update({
                # Required settings from our config
                'AUTHOR': pelican_config.get('author', 'Unknown Author'),
                'SITENAME': pelican_config.get('sitename', 'My Site'),
                'SITEURL': pelican_config.get('site_url', ''),
                'PATH': str(content_dir),
                'OUTPUT_PATH': str(base_dir / site_config.get('output_dir', 'output')),
                'THEME': pelican_config.get('theme', 'notmyidea'),

                # File handling settings
                'DELETE_OUTPUT_DIRECTORY': pelican_config.get('delete_output_directory', False),
                'IGNORE_FILES': pelican_config.get('ignore_files', ['.#*', '__pycache__', '*~', '*.pyc']),
                'STATIC_PATHS': pelican_config.get('static_paths', ['images']),

                # Content organization
                'ARTICLE_PATHS': pelican_config.get('article_paths', ['']),
                'PAGE_PATHS': pelican_config.get('page_paths', ['pages']),

                # Locale and language settings
                'TIMEZONE': pelican_config.get('timezone', 'UTC'),
                'DEFAULT_LANG': pelican_config.get('default_lang', 'en'),

                # Pagination
                'DEFAULT_PAGINATION': pelican_config.get('default_pagination', False),
            })

            # Use Pelican's configure_settings to finalize configuration
            pelican_settings = configure_settings(pelican_settings_dict)

            pelican_instance = pelican.Pelican(pelican_settings)
            pelican_instance.run()
            
            return True
            
        except Exception as e:
            raise PelicanError(f"Pelican generation failed: {e}") from e