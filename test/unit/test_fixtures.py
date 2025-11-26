"""Tests to verify fixture functionality."""

import json


class TestFixtures:
    """Test that our fixtures work correctly."""

    def test_temp_filesystem_fixture(self, temp_filesystem):
        """Test that temp_filesystem fixture creates temporary directory."""
        assert temp_filesystem.exists()
        assert temp_filesystem.is_dir()

    def test_file_factory_creates_text_file(self, file_factory):
        """Test file_factory creates text files."""
        file_path = file_factory("test.txt", content="Hello World")

        assert file_path.exists()
        assert file_path.read_text() == "Hello World"

    def test_file_factory_creates_json_file(self, file_factory):
        """Test file_factory creates JSON files."""
        test_data = {"key": "value", "number": 42}
        file_path = file_factory("test.json", json_content=test_data)

        assert file_path.exists()
        loaded_data = json.loads(file_path.read_text())
        assert loaded_data == test_data

    def test_directory_factory_creates_directories(self, directory_factory):
        """Test directory_factory creates nested directories."""
        dir_path = directory_factory("deep/nested/directory")

        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_config_file_factory_creates_config(self, config_file_factory):
        """Test config_file_factory creates config files with defaults."""
        config_path = config_file_factory("site")

        assert config_path.exists()
        assert config_path.name == "site.json"

        # Should contain default site config
        config_data = json.loads(config_path.read_text())
        assert "output_dir" in config_data
        assert "base_url" in config_data

    def test_full_config_setup_creates_all_configs(self, full_config_setup, temp_filesystem):
        """Test full_config_setup creates all required config files."""
        configs = full_config_setup()

        assert len(configs) == 4
        assert "site" in configs
        assert "normpic" in configs
        assert "pelican" in configs
        assert "galleria" in configs

        # All config files should exist
        for config_name, config_path in configs.items():
            assert config_path.exists()
            assert config_path.suffix == ".json"

        # Config directory should exist
        config_dir = temp_filesystem / "config"
        assert config_dir.exists()
        assert config_dir.is_dir()
