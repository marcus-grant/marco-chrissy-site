"""NormPic integration functionality."""

from dataclasses import dataclass
from typing import List


@dataclass
class OrganizeResult:
    """Result of photo organization operation."""
    success: bool
    errors: List[str]