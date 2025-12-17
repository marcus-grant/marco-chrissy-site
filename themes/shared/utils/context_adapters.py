"""Context adapters for converting system-specific contexts to shared template format."""

import json
from abc import ABC, abstractmethod
from typing import Any


class BaseContextAdapter(ABC):
    """Base class for context adapters."""

    @abstractmethod
    def to_shared_context(self) -> dict[str, Any]:
        """Convert system-specific context to shared template context.

        Returns:
            Dict with standardized context keys for shared templates
        """
        raise NotImplementedError


class PelicanContextAdapter(BaseContextAdapter):
    """Adapter for converting Pelican context to shared format."""

    def __init__(self, pelican_context: dict[str, Any]):
        """Initialize with Pelican template context."""
        self.context = pelican_context

    def to_shared_context(self) -> dict[str, Any]:
        """Convert Pelican context to shared format."""
        page = self.context.get('page', {})

        # Convert MENUITEMS to standard navigation format
        navigation_items = []
        for title, url in self.context.get('MENUITEMS', []):
            navigation_items.append({'title': title, 'url': url})

        return {
            'page_type': 'static',
            'current_url': page.get('url', '/'),
            'site_name': self.context.get('SITENAME', ''),
            'navigation_items': navigation_items,
            'page_title': page.get('title', ''),
        }


class GalleriaContextAdapter(BaseContextAdapter):
    """Adapter for converting Galleria context to shared format."""

    def __init__(self, galleria_context: dict[str, Any]):
        """Initialize with Galleria template context."""
        self.context = galleria_context

    def to_shared_context(self) -> dict[str, Any]:
        """Convert Galleria context to shared format."""
        return {
            'page_type': 'gallery',
            'current_url': self.context.get('gallery_url', '/'),
            'site_name': self.context.get('collection_name', ''),
            'gallery_context': {
                'name': self.context.get('collection_name', ''),
                'current_page': self.context.get('current_page', 1),
                'total_pages': self.context.get('total_pages', 1),
            },
        }


def load_navigation_config(config_path: str) -> dict[str, list[dict[str, str]]]:
    """Load navigation configuration from JSON file.

    Args:
        config_path: Path to navigation configuration file

    Returns:
        Navigation configuration dict
    """
    with open(config_path) as f:
        return json.load(f)
