"""Unit tests for serializer data models."""


class TestPhoto:
    """Unit tests for Photo model class."""

    def test_photo_creation_with_required_fields_only(self):
        """Test Photo creation with only required fields."""
        from galleria.serializer.models import Photo

        photo = Photo(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
        )

        assert photo.source_path == "/path/to/source.jpg"
        assert photo.dest_path == "/path/to/dest.jpg"
        assert photo.hash == "abc123def456"
        assert photo.size_bytes == 1024
        assert photo.mtime == 1699123456.789
        assert photo.camera is None
        assert photo.gps is None

    def test_photo_creation_with_all_fields(self):
        """Test Photo creation with all fields including optionals."""
        from galleria.serializer.models import Photo

        gps_data = {"lat": 40.7128, "lon": -74.0060}

        photo = Photo(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=2048000,
            mtime=1699123456.789,
            camera="Canon EOS R5",
            gps=gps_data,
        )

        assert photo.source_path == "/path/to/source.jpg"
        assert photo.dest_path == "/path/to/dest.jpg"
        assert photo.hash == "abc123def456"
        assert photo.size_bytes == 2048000
        assert photo.mtime == 1699123456.789
        assert photo.camera == "Canon EOS R5"
        assert photo.gps == gps_data

    def test_photo_with_none_optional_fields(self):
        """Test Photo creation with explicitly None optional fields."""
        from galleria.serializer.models import Photo

        photo = Photo(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123",
            size_bytes=512,
            mtime=1699123456.0,
            camera=None,
            gps=None,
        )

        assert photo.camera is None
        assert photo.gps is None


class TestPhotoCollection:
    """Unit tests for PhotoCollection model class."""

    def test_photo_collection_creation_with_name_only(self):
        """Test PhotoCollection creation with only name."""
        from galleria.serializer.models import PhotoCollection

        collection = PhotoCollection(name="test-collection")

        assert collection.name == "test-collection"
        assert collection.description is None
        assert collection.photos == []

    def test_photo_collection_creation_with_all_fields(self):
        """Test PhotoCollection creation with all fields."""
        from galleria.serializer.models import Photo, PhotoCollection

        photos = [
            Photo(
                source_path="/path/to/photo1.jpg",
                dest_path="/path/to/dest1.jpg",
                hash="hash1",
                size_bytes=1024,
                mtime=1699123456.789,
            ),
            Photo(
                source_path="/path/to/photo2.jpg",
                dest_path="/path/to/dest2.jpg",
                hash="hash2",
                size_bytes=2048,
                mtime=1699123457.123,
            ),
        ]

        collection = PhotoCollection(
            name="wedding-photos",
            description="John and Jane's wedding",
            photos=photos,
        )

        assert collection.name == "wedding-photos"
        assert collection.description == "John and Jane's wedding"
        assert len(collection.photos) == 2
        assert collection.photos[0].source_path == "/path/to/photo1.jpg"
        assert collection.photos[1].source_path == "/path/to/photo2.jpg"

    def test_photo_collection_with_empty_photos_list(self):
        """Test PhotoCollection creation with explicitly empty photos list."""
        from galleria.serializer.models import PhotoCollection

        collection = PhotoCollection(
            name="empty-collection",
            description="A collection with no photos",
            photos=[],
        )

        assert collection.name == "empty-collection"
        assert collection.description == "A collection with no photos"
        assert collection.photos == []

    def test_photo_collection_photos_default_to_empty_list(self):
        """Test that photos defaults to empty list when None is passed."""
        from galleria.serializer.models import PhotoCollection

        collection = PhotoCollection(name="test", photos=None)

        assert collection.photos == []
        assert isinstance(collection.photos, list)
