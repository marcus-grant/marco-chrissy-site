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
                
                # Enable jinja2content plugin for template includes in Markdown
                'PLUGINS': ['jinja2content'],

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
            if 'THEME_TEMPLATE_OVERRIDES' in pelican_config:
                # Create temporary config file for configure_pelican_shared_templates
                import json
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
                    json.dump(pelican_config, temp_config)
                    temp_config_path = temp_config.name
                
                try:
                    # Use configure_pelican_shared_templates for proper template precedence
                    template_dirs = configure_pelican_shared_templates(temp_config_path)
                    if template_dirs:
                        # Convert relative paths to absolute paths for proper resolution
                        absolute_template_dirs = []
                        for template_dir in template_dirs:
                            if not Path(template_dir).is_absolute():
                                absolute_path = str(base_dir / template_dir)
                            else:
                                absolute_path = template_dir
                            absolute_template_dirs.append(absolute_path)
                        
                        # Set template paths for theme templates
                        pelican_settings_dict['THEME_TEMPLATES_OVERRIDES'] = absolute_template_dirs
                        # Set template paths for jinja2content plugin (for includes in Markdown)
                        pelican_settings_dict['JINJA2CONTENT_TEMPLATES'] = absolute_template_dirs
                        
                        # Configure shared static paths for CSS/assets
                        shared_static_path = str(base_dir / pelican_config['THEME_TEMPLATE_OVERRIDES'] / 'static')
                        if Path(shared_static_path).exists():
                            # Add shared static path to THEME_STATIC_PATHS
                            existing_static_paths = pelican_settings_dict.get('THEME_STATIC_PATHS', ['static'])
                            if isinstance(existing_static_paths, str):
                                existing_static_paths = [existing_static_paths]
                            pelican_settings_dict['THEME_STATIC_PATHS'] = existing_static_paths + [shared_static_path]
                            
                            # Auto-configure shared CSS files for HTML inclusion
                            shared_css_dir = Path(shared_static_path) / 'css'
                            if shared_css_dir.exists():
                                css_files = list(shared_css_dir.glob('*.css'))
                                if css_files:
                                    # Use first shared CSS file as main theme CSS
                                    css_filename = css_files[0].name
                                    pelican_settings_dict['CSS_FILE'] = css_filename
                                    # Also set the theme to use the shared templates
                                    if absolute_template_dirs:
                                        pelican_settings_dict['THEME'] = str(base_dir / pelican_config['THEME_TEMPLATE_OVERRIDES'])
                finally:
                    # Clean up temporary file
                    Path(temp_config_path).unlink(missing_ok=True)
            
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