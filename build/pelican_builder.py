"""PelicanBuilder for extracting pelican generation logic."""

import subprocess
import tempfile
from pathlib import Path

import pelican
import jinja2
from pelican.settings import DEFAULT_CONFIG, configure_settings
from .exceptions import PelicanError
from defaults import get_shared_template_paths
from themes.shared.utils.template_loader import configure_pelican_shared_templates


class PelicanBuilder:
    """Handles pelican site generation."""

    def __init__(self):
        """Initialize PelicanBuilder."""
        pass

    def build(self, site_config: dict, pelican_config: dict, base_dir: Path, override_site_url: str | None = None) -> bool:
        """Build pelican site using configuration.
        
        Args:
            site_config: Site configuration dict
            pelican_config: Pelican configuration dict
            base_dir: Base directory for resolving paths
            override_site_url: Optional URL override for development (defaults to None)
            
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
            
            # Check if there's content with slug 'index' that would conflict with default index
            has_index_content = False
            if content_dir.exists():
                for content_file in content_dir.glob('**/*.md'):
                    content_text = content_file.read_text()
                    if 'slug: index' in content_text:
                        has_index_content = True
                        break

            # Start with Pelican's full default configuration
            pelican_settings_dict = DEFAULT_CONFIG.copy()

            # Override with our specific settings
            pelican_settings_dict.update({
                # Required settings from our config
                'AUTHOR': pelican_config.get('author', 'Unknown Author'),
                'SITENAME': pelican_config.get('sitename', 'My Site'),
                'SITEURL': override_site_url or pelican_config.get('site_url', ''),
                'PATH': str(content_dir),
                'OUTPUT_PATH': str(base_dir / site_config.get('output_dir', 'output')),
                'THEME': pelican_config.get('theme', 'notmyidea'),

                # File handling settings - allow overwriting existing files  
                'DELETE_OUTPUT_DIRECTORY': False,
                'OUTPUT_RETENTION': ['galleries'],  # Keep existing gallery files
                'CACHE_CONTENT': False,  # Disable caching to avoid conflicts
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
                
                # Index page configuration - avoid slug conflicts
                'DIRECT_TEMPLATES': ['index', 'archives', 'tags', 'categories'],
                'INDEX_SAVE_AS': '' if has_index_content else 'index.html',
            })
            
            # Configure shared template paths only when explicitly provided
            if 'SHARED_THEME_PATH' in pelican_config:
                shared_path = Path(pelican_config['SHARED_THEME_PATH'])
                shared_templates_dir = shared_path / 'templates'
                
                if shared_templates_dir.exists():
                    pelican_settings_dict['JINJA_ENVIRONMENT'] = {
                        'loader': jinja2.FileSystemLoader([str(shared_templates_dir)])
                    }
            
            # Remove any existing index.html that would conflict with Pelican
            output_path = base_dir / site_config.get('output_dir', 'output')
            index_path = output_path / 'index.html'
            if index_path.exists():
                index_path.unlink()
                
            # Also clean up any feed files that might cause conflicts
            for feed_file in output_path.glob('feeds/*.xml'):
                if feed_file.exists():
                    feed_file.unlink()
            feeds_dir = output_path / 'feeds'
            if feeds_dir.exists() and not any(feeds_dir.iterdir()):
                feeds_dir.rmdir()

            # Use Pelican's configure_settings to finalize configuration
            pelican_settings = configure_settings(pelican_settings_dict)

            pelican_instance = pelican.Pelican(pelican_settings)
            pelican_instance.run()
            
            return True
            
        except Exception as e:
            raise PelicanError(f"Pelican generation failed: {e}") from e