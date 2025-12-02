"""Data models for photo collections."""


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
