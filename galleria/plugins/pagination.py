"""Pagination plugin implementation for splitting photos into pages."""

from .base import PluginContext, PluginResult
from .interfaces import TransformPlugin


class BasicPaginationPlugin(TransformPlugin):
    """Basic pagination plugin for splitting photo collections into pages."""

    @property
    def name(self) -> str:
        return "basic-pagination"

    @property
    def version(self) -> str:
        return "1.0.0"

    def transform_data(self, context: PluginContext) -> PluginResult:
        """Transform photo data by splitting into paginated pages."""
        try:
            # Get configuration - support both nested and direct config patterns
            config = context.config or {}
            
            # Try nested config first (for multi-stage pipelines), fall back to direct access
            if "transform" in config:
                transform_config = config["transform"]
            else:
                transform_config = config
                
            page_size = transform_config.get("page_size", 20)
            
            # Validate page_size configuration
            if page_size <= 0:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["INVALID_PAGE_SIZE: page_size must be positive"]
                )
            
            if page_size > 100:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["INVALID_PAGE_SIZE: page_size must be <= 100"]
                )

            # Get input data
            photos = context.input_data.get("photos", [])
            collection_name = context.input_data.get("collection_name", "")
            
            # Calculate number of pages needed
            total_photos = len(photos)
            total_pages = (total_photos + page_size - 1) // page_size if total_photos > 0 else 1
            
            # Split photos into pages
            pages = []
            if total_photos == 0:
                # Create one empty page for empty collections
                pages.append([])
            else:
                for i in range(0, len(photos), page_size):
                    page_photos = photos[i:i + page_size]
                    pages.append(page_photos)
            
            transform_metadata = {
                "page_size": page_size,
                "total_pages": total_pages,
                "total_photos": total_photos
            }
            
            # Add page numbers to metadata if there are multiple pages
            if total_pages > 1:
                transform_metadata["pagination_enabled"] = True
                transform_metadata["page_info"] = [
                    {
                        "page_number": i + 1,
                        "photo_count": len(pages[i]),
                        "start_index": i * page_size,
                        "end_index": min((i + 1) * page_size - 1, total_photos - 1)
                    }
                    for i in range(total_pages)
                ]
            else:
                transform_metadata["pagination_enabled"] = False

            return PluginResult(
                success=True,
                output_data={
                    "pages": pages,
                    "collection_name": collection_name,
                    "transform_metadata": transform_metadata,
                    # Pass through other processor data
                    **{k: v for k, v in context.input_data.items() 
                       if k not in ["photos", "collection_name"]}
                }
            )

        except Exception as e:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"PAGINATION_ERROR: {str(e)}"]
            )


class SmartPaginationPlugin(TransformPlugin):
    """Smart pagination plugin with adaptive page sizing and photo balancing."""

    @property
    def name(self) -> str:
        return "smart-pagination"

    @property
    def version(self) -> str:
        return "1.0.0"

    def transform_data(self, context: PluginContext) -> PluginResult:
        """Transform photo data using intelligent pagination strategies."""
        try:
            # Get configuration - support both nested and direct config patterns
            config = context.config or {}
            
            # Try nested config first (for multi-stage pipelines), fall back to direct access
            if "transform" in config:
                transform_config = config["transform"]
            else:
                transform_config = config
                
            target_page_size = transform_config.get("page_size", 20)
            max_page_size = transform_config.get("max_page_size", target_page_size * 1.5)
            min_page_size = transform_config.get("min_page_size", max(1, target_page_size // 2))
            balance_pages = transform_config.get("balance_pages", True)
            
            # Validate configuration
            if target_page_size <= 0:
                return PluginResult(
                    success=False,
                    output_data={},
                    errors=["INVALID_PAGE_SIZE: page_size must be positive"]
                )

            photos = context.input_data.get("photos", [])
            collection_name = context.input_data.get("collection_name", "")
            total_photos = len(photos)
            
            if total_photos == 0:
                # Handle empty collection
                return PluginResult(
                    success=True,
                    output_data={
                        "pages": [],
                        "collection_name": collection_name,
                        "transform_metadata": {
                            "page_size": target_page_size,
                            "total_pages": 0,
                            "total_photos": 0,
                            "pagination_enabled": False,
                            "pagination_strategy": "empty"
                        }
                    }
                )

            # Calculate optimal pagination
            if balance_pages and total_photos > target_page_size:
                pages = self._balance_pagination(
                    photos, target_page_size, min_page_size, max_page_size
                )
                strategy = "balanced"
            else:
                # Simple pagination - calculate pages needed first
                total_pages = (total_photos + target_page_size - 1) // target_page_size if total_photos > 0 else 1
                pages = []
                for i in range(0, total_photos, target_page_size):
                    pages.append(photos[i:i + target_page_size])
                strategy = "simple"

            # For balanced pagination, total_pages is calculated by the balancing algorithm
            if balance_pages and total_photos > target_page_size:
                total_pages = len(pages)  # Keep existing logic for balanced case
            actual_page_sizes = [len(page) for page in pages]
            
            transform_metadata = {
                "page_size": target_page_size,
                "total_pages": total_pages,
                "total_photos": total_photos,
                "pagination_enabled": total_pages > 1,
                "pagination_strategy": strategy,
                "actual_page_sizes": actual_page_sizes,
                "avg_page_size": sum(actual_page_sizes) / len(actual_page_sizes) if actual_page_sizes else 0
            }

            return PluginResult(
                success=True,
                output_data={
                    "pages": pages,
                    "collection_name": collection_name,
                    "transform_metadata": transform_metadata,
                    # Pass through other processor data
                    **{k: v for k, v in context.input_data.items() 
                       if k not in ["photos", "collection_name"]}
                }
            )

        except Exception as e:
            return PluginResult(
                success=False,
                output_data={},
                errors=[f"SMART_PAGINATION_ERROR: {str(e)}"]
            )

    def _balance_pagination(
        self, 
        photos: list, 
        target_size: int, 
        min_size: int, 
        max_size: int
    ) -> list[list]:
        """Balance photos across pages to avoid small last pages."""
        total_photos = len(photos)
        
        # Calculate number of pages needed
        estimated_pages = (total_photos + target_size - 1) // target_size
        
        # If last page would be too small, redistribute
        if total_photos % target_size < min_size and estimated_pages > 1:
            # Redistribute photos to balance page sizes
            photos_per_page = total_photos // estimated_pages
            extra_photos = total_photos % estimated_pages
            
            pages = []
            current_index = 0
            
            for page_num in range(estimated_pages):
                # Some pages get one extra photo
                page_size = photos_per_page + (1 if page_num < extra_photos else 0)
                
                # Ensure page size is within bounds
                page_size = max(min_size, min(page_size, max_size))
                
                pages.append(photos[current_index:current_index + page_size])
                current_index += page_size
                
                if current_index >= total_photos:
                    break
            
            return pages
        else:
            # Simple chunking is fine
            pages = []
            for i in range(0, total_photos, target_size):
                pages.append(photos[i:i + target_size])
            return pages