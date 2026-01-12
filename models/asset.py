"""Asset data models"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AssetRecord:
    """Record of a generated asset for tracking and viewing"""
    asset_id: str
    asset_url: str
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    bytes_size: int
    sha256: Optional[str]  # Content hash for deduplication
    created_at: datetime
    workflow_id: str
    prompt_id: str
    expires_at: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)
