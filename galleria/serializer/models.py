"""Data models for photo collections.

These typed models are intended to be galleria's internal representation,
providing type safety when galleria is extracted as a standalone project.

NOTE: Currently unused in the plugin pipeline (plugins use dicts).
See galleria/serializer/__init__.py for status and future plans.
"""


class Photo:
    """Individual photo data structure."""

    def __init__(
        self, source_path, dest_path, hash, size_bytes, mtime, camera=None, gps=None
    ):
        self.source_path = source_path
        self.dest_path = dest_path
        self.hash = hash
        self.size_bytes = size_bytes
        self.mtime = mtime
        self.camera = camera
        self.gps = gps


class PhotoCollection:
    """Simple photo collection data structure."""

    def __init__(self, name, description=None, photos=None):
        self.name = name
        self.description = description
        self.photos = photos or []
