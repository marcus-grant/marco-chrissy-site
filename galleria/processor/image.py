"""Image processor for generating optimized thumbnails."""

from pathlib import Path

from PIL import Image


class ImageProcessingError(Exception):
    """Exception raised when image processing fails."""

    pass


class ImageProcessor:
    """Processor for generating optimized WebP thumbnails from images."""

    def process_image(
        self, source_path, output_dir, size=400, quality=85, output_name=None
    ):
        """Process a single image to generate a WebP thumbnail.

        Args:
            source_path: Path to source image file
            output_dir: Directory to save thumbnail
            size: Thumbnail size (creates square thumbnail)
            quality: WebP quality setting (0-100)
            output_name: Optional custom output name (defaults to source stem)

        Returns:
            Path to generated thumbnail

        Raises:
            ImageProcessingError: If processing fails
        """
        source_path = Path(source_path)
        output_dir = Path(output_dir)

        # Validate source file exists
        if not source_path.exists():
            raise ImageProcessingError(f"Source file does not exist: {source_path}")

        try:
            # Load image
            img = Image.open(source_path)

            # Convert to RGB if needed (for RGBA, grayscale, etc.)
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Apply center crop to square
            img_cropped = self._center_crop_to_square(img)

            # Resize to target size
            img_resized = img_cropped.resize((size, size), Image.Resampling.LANCZOS)

            # Determine output filename
            if output_name is None:
                output_name = source_path.stem + ".webp"
            elif not output_name.endswith(".webp"):
                output_name = output_name + ".webp"

            output_path = output_dir / output_name

            # Save as WebP
            img_resized.save(output_path, "WEBP", quality=quality)

            return output_path

        except OSError as e:
            raise ImageProcessingError(
                f"Failed to process image {source_path}: {e}"
            ) from e

    def _center_crop_to_square(self, img):
        """Crop image to square using center crop strategy.

        Args:
            img: PIL Image object

        Returns:
            PIL Image object (cropped to square)
        """
        width, height = img.size

        if width == height:
            # Already square
            return img

        # Calculate center crop box
        if width > height:
            # Landscape: crop width
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        else:
            # Portrait: crop height
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width

        return img.crop((left, top, right, bottom))

    def should_process(self, source_path, thumbnail_path):
        """Check if image should be processed (naive caching).

        Args:
            source_path: Path to source image
            thumbnail_path: Path to thumbnail

        Returns:
            True if should process, False if cached thumbnail is valid
        """
        source_path = Path(source_path)
        thumbnail_path = Path(thumbnail_path)

        # If thumbnail doesn't exist, must process
        if not thumbnail_path.exists():
            return True

        # Compare modification times (naive caching)
        source_mtime = source_path.stat().st_mtime
        thumbnail_mtime = thumbnail_path.stat().st_mtime

        # If source is newer than thumbnail, must reprocess
        return source_mtime > thumbnail_mtime

    def process_collection(
        self, collection, output_dir, size=400, quality=85, progress_callback=None
    ):
        """Process a photo collection to generate thumbnails.

        Args:
            collection: PhotoCollection object with photos to process
            output_dir: Directory to save thumbnails
            size: Thumbnail size (default 400)
            quality: WebP quality setting (default 85)
            progress_callback: Optional callback(current, total, photo_path)

        Returns:
            List of result dictionaries with processing status
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        total = len(collection.photos)

        for i, photo in enumerate(collection.photos, start=1):
            source_path = Path(photo.source_path)
            dest_name = Path(photo.dest_path).stem + ".webp"
            thumbnail_path = output_dir / dest_name

            # Report progress
            if progress_callback:
                progress_callback(i, total, str(source_path))

            # Check cache
            if not self.should_process(source_path, thumbnail_path):
                results.append(
                    {
                        "source_path": str(source_path),
                        "thumbnail_path": str(thumbnail_path),
                        "cached": True,
                    }
                )
                continue

            # Process image
            try:
                result_path = self.process_image(
                    source_path,
                    output_dir,
                    size=size,
                    quality=quality,
                    output_name=dest_name,
                )
                results.append(
                    {
                        "source_path": str(source_path),
                        "thumbnail_path": str(result_path),
                        "cached": False,
                    }
                )
            except ImageProcessingError as e:
                results.append({"source_path": str(source_path), "error": str(e)})

        return results
