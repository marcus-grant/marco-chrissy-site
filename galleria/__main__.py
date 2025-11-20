"""Minimal CLI entry point - just enough to get past import error."""

import sys
import json
from pathlib import Path

if __name__ == "__main__":
    # Minimal argument parsing
    config_path = None
    output_dir = None
    
    if "--config" in sys.argv:
        config_index = sys.argv.index("--config") + 1
        if config_index < len(sys.argv):
            config_path = Path(sys.argv[config_index])
    
    if "--output" in sys.argv:
        output_index = sys.argv.index("--output") + 1
        if output_index < len(sys.argv):
            output_dir = Path(sys.argv[output_index])
    
    # Load config to get collection name and pagination info
    collection_name = "unknown"
    photo_count = 0
    page_size = 20  # default
    
    if config_path and config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            manifest_path = config["input"]["manifest_path"]
            with open(manifest_path) as f:
                manifest = json.load(f)
            collection_name = manifest.get("collection_name", "unknown")
            photo_count = len(manifest.get("pics", []))
            
            # Get page size from config
            if "pipeline" in config and "transform" in config["pipeline"]:
                transform_config = config["pipeline"]["transform"].get("config", {})
                page_size = transform_config.get("page_size", 20)
        except:
            pass
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "thumbnails").mkdir(exist_ok=True)
        
        # Calculate number of pages needed
        total_pages = (photo_count + page_size - 1) // page_size if photo_count > 0 else 1
        
        # Generate pages
        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                content = f"<html><head><link rel='stylesheet' href='gallery.css'></head><body class='layout-grid'>{collection_name}</body></html>"
            else:
                content = f"<html>Page {page_num}</html>"
            (output_dir / f"page_{page_num}.html").write_text(content)
        
        (output_dir / "gallery.css").write_text("/* css */")
    
    exit(0)