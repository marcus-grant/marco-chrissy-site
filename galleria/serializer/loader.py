"""Photo collection loader."""

import json
from pathlib import Path

from .exceptions import ManifestNotFoundError, ManifestValidationError
from .models import Photo, PhotoCollection


def load_photo_collection(manifest_path: str):
    """Load photo collection from manifest path."""
    path = Path(manifest_path)

    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise ManifestNotFoundError(f"Manifest file not found: {manifest_path}") from e

    # Validate required fields
    if "collection_name" not in data:
        raise ManifestValidationError("Missing required field: collection_name")

    # Convert pics to Photo objects
    photos = []
    for pic_data in data.get("pics", []):
        photo = Photo(
            source_path=pic_data["source_path"],
            dest_path=pic_data["dest_path"],
            hash=pic_data["hash"],
            size_bytes=pic_data["size_bytes"],
            mtime=pic_data["mtime"],
            camera=pic_data.get("camera"),
            gps=pic_data.get("gps"),
        )
        photos.append(photo)

    return PhotoCollection(
        name=data["collection_name"],
        description=data.get("collection_description"),
        photos=photos,
    )
