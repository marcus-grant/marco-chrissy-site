"""NormPic provider plugin for loading photo collections from NormPic manifest files."""

import json
from pathlib import Path

from galleria.plugins.base import PluginContext, PluginResult
from galleria.plugins.interfaces import ProviderPlugin


class NormPicProviderPlugin(ProviderPlugin):
    """Provider plugin for loading NormPic manifest files.

    Converts NormPic manifest.json format to ProviderPlugin contract format.
    This replaces the previous galleria.serializer.loader functionality with
    the new plugin system architecture.
    """

    @property
    def name(self) -> str:
        """Plugin name identifier."""
        return "normpic-provider"

    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"

    def load_collection(self, context: PluginContext) -> PluginResult:
        """Load photo collection from NormPic manifest.json file.

        Args:
            context: Plugin execution context containing:
                - input_data: {"manifest_path": str} - Path to NormPic manifest.json
                - config: Optional configuration parameters
                - output_dir: Target output directory

        Returns:
            PluginResult with success/failure and photo collection data

        Expected output format follows ProviderPlugin contract:
        {
            "photos": [
                {
                    "source_path": str,  # Original photo file path
                    "dest_path": str,    # Destination relative path
                    "metadata": {        # NormPic metadata fields
                        "hash": str,
                        "size_bytes": int,
                        "mtime": float,
                        "camera": str,      # Optional
                        "gps": dict,        # Optional
                        ...                 # Other NormPic fields
                    }
                },
                ...
            ],
            "collection_name": str,        # From manifest collection_name
            "collection_description": str, # From manifest (optional)
            "manifest_version": str        # From manifest (optional)
        }
        """
        try:
            # Extract manifest path from input data
            if "manifest_path" not in context.input_data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required input: manifest_path"]
                )

            manifest_path = Path(context.input_data["manifest_path"])

            # Load and parse manifest JSON
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
            except FileNotFoundError:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=[f"Manifest file not found: {manifest_path}"]
                )
            except json.JSONDecodeError as e:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=[f"Invalid JSON in manifest: {e}"]
                )

            # Validate required fields
            if "collection_name" not in data:
                return PluginResult(
                    success=False,
                    output_data=None,
                    errors=["Missing required field: collection_name"]
                )

            # Convert NormPic pics to ProviderPlugin photo format
            photos = []
            pics_data = data.get("pics", [])

            for pic_data in pics_data:
                try:
                    # Extract required NormPic fields
                    source_path = pic_data["source_path"]
                    dest_path = pic_data["dest_path"]

                    # Create metadata dict with all NormPic fields except source/dest paths
                    metadata = {}
                    for key, value in pic_data.items():
                        if key not in ["source_path", "dest_path"]:
                            metadata[key] = value

                    # Build photo object following ProviderPlugin contract
                    photo = {
                        "source_path": source_path,
                        "dest_path": dest_path,
                        "metadata": metadata
                    }
                    photos.append(photo)

                except KeyError as e:
                    return PluginResult(
                        success=False,
                        output_data=None,
                        errors=[f"Missing required pic field: {e}"]
                    )

            # Build output data following ProviderPlugin contract
            output_data = {
                "photos": photos,
                "collection_name": data["collection_name"]
            }

            # Add optional fields if present
            if "collection_description" in data:
                output_data["collection_description"] = data["collection_description"]
            if "manifest_version" in data:
                output_data["manifest_version"] = data["manifest_version"]

            return PluginResult(
                success=True,
                output_data=output_data
            )

        except Exception as e:
            # Catch any unexpected errors
            return PluginResult(
                success=False,
                output_data=None,
                errors=[f"Unexpected error loading NormPic manifest: {e}"]
            )
