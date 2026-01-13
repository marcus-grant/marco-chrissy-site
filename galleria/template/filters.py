"""Jinja2 template filters for URL generation with context awareness."""

import os

from build.context import BuildContext


def full_url(path: str, context: BuildContext, site_url: str) -> str:
    """Generate relative URL from path for use with Edge Rules routing.

    Args:
        path: File path (absolute or relative)
        context: BuildContext (unused but kept for compatibility)
        site_url: Site URL (unused but kept for compatibility)

    Returns:
        Relative URL starting with / for Edge Rules routing
    """
    if not path:
        return path

    # Convert absolute paths to relative web paths
    web_path = _make_relative_path(path)

    # Ensure web_path starts with /
    if web_path and not web_path.startswith('/'):
        web_path = '/' + web_path

    return web_path


def _make_relative_path(path: str) -> str:
    """Convert filesystem path to relative web path.

    Args:
        path: File path (absolute or relative, e.g., output/galleries/wedding/thumbnails/img.webp)

    Returns:
        Relative web path (e.g., galleries/wedding/thumbnails/img.webp)
    """
    if not path:
        return path

    # Normalize path separators and split into parts
    normalized_path = path.replace(os.sep, '/')
    path_parts = normalized_path.split('/')

    # Try to find and strip 'output' directory (the web root)
    try:
        output_index = path_parts.index('output')
        # Get everything after 'output'
        relative_parts = path_parts[output_index + 1:]
        relative_path = '/'.join(relative_parts)

        # Ensure photos go to pics/full/ subdirectory for production use case
        if (relative_path.startswith('pics/') and
            not relative_path.startswith('pics/full/') and
            not relative_path.startswith('pics/web/') and
            relative_path.lower().endswith(('.jpg', '.jpeg'))):
            # Move photos from pics/ to pics/full/
            filename = os.path.basename(relative_path)
            relative_path = f'pics/full/{filename}'

        return relative_path
    except ValueError:
        # 'output' not found in path, fall through to file type detection
        pass

    # For paths without 'output', check if it needs file type detection
    # Only apply file type detection if it's a bare filename (no directory separators)
    if os.sep not in path and '/' not in path:
        # This is a bare filename, apply file type detection
        filename = os.path.basename(path)

        # For photos (jpg, jpeg), they should be in pics/full/
        if filename.lower().endswith(('.jpg', '.jpeg')):
            return f'pics/full/{filename}'
        # For thumbnails (webp), they should be in galleries/{collection}/thumbnails/
        elif filename.lower().endswith('.webp'):
            # Without collection context, fallback to thumbnails/
            return f'thumbnails/{filename}'
        else:
            # Fallback to just filename
            return filename
    else:
        # This is a relative path with directory structure, preserve it
        return path
