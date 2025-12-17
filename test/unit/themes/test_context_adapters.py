"""Unit tests for shared template context adapters."""

import pytest


class TestContextAdapters:
    """Test context adapter functionality."""

    def test_base_context_adapter_interface(self):
        """Test base context adapter defines proper interface."""
        from themes.shared.utils.context_adapters import BaseContextAdapter

        # Should be abstract class
        with pytest.raises(TypeError):
            BaseContextAdapter()

        # Should define abstract method
        assert hasattr(BaseContextAdapter, 'to_shared_context')

    def test_pelican_context_adapter(self, shared_theme_dirs, file_factory):
        """Test Pelican context adapter converts Pelican context to shared format."""
        from themes.shared.utils.context_adapters import PelicanContextAdapter

        # Create mock Pelican context
        pelican_context = {
            'SITENAME': 'Test Site',
            'SITEURL': 'https://example.com',
            'page': {
                'title': 'About Us',
                'url': '/about/',
                'slug': 'about'
            },
            'MENUITEMS': [
                ('Home', '/'),
                ('About', '/about/'),
                ('Galleries', '/galleries/')
            ]
        }

        adapter = PelicanContextAdapter(pelican_context)
        shared_context = adapter.to_shared_context()

        # Should convert to shared context format
        assert shared_context['page_type'] == 'static'
        assert shared_context['current_url'] == '/about/'
        assert shared_context['site_name'] == 'Test Site'
        assert shared_context['navigation_items'] == [
            {'title': 'Home', 'url': '/'},
            {'title': 'About', 'url': '/about/'},
            {'title': 'Galleries', 'url': '/galleries/'}
        ]

    def test_galleria_context_adapter(self):
        """Test Galleria context adapter converts Galleria context to shared format."""
        from themes.shared.utils.context_adapters import GalleriaContextAdapter

        # Create mock Galleria context
        galleria_context = {
            'collection_name': 'Wedding Photos',
            'current_page': 2,
            'total_pages': 5,
            'gallery_url': '/galleries/wedding/',
            'photos': [{'filename': 'IMG_001.jpg'}]
        }

        adapter = GalleriaContextAdapter(galleria_context)
        shared_context = adapter.to_shared_context()

        # Should convert to shared context format
        assert shared_context['page_type'] == 'gallery'
        assert shared_context['current_url'] == '/galleries/wedding/'
        assert shared_context['site_name'] == 'Wedding Photos'
        assert shared_context['gallery_context'] == {
            'name': 'Wedding Photos',
            'current_page': 2,
            'total_pages': 5
        }

    def test_context_adapter_with_navigation_config(self, file_factory):
        """Test context adapters can load navigation from config."""
        from themes.shared.utils.context_adapters import load_navigation_config

        # Create navigation config
        nav_config = file_factory(
            "config/navigation.json",
            json_content={
                "primary": [
                    {"title": "Home", "url": "/"},
                    {"title": "About", "url": "/about/"},
                    {"title": "Galleries", "url": "/galleries/"}
                ]
            }
        )

        navigation = load_navigation_config(str(nav_config))

        assert len(navigation['primary']) == 3
        assert navigation['primary'][0]['title'] == 'Home'
