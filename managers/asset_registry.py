"""Asset registry for tracking generated assets"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from models.asset import AssetRecord

logger = logging.getLogger("MCP_Server")


class AssetRegistry:
    """Manages tracking of generated assets for inline viewing"""
    
    def __init__(self, ttl_hours: int = 24):
        self._assets: Dict[str, AssetRecord] = {}
        self._url_to_asset_id: Dict[str, str] = {}  # For deduplication
        self.ttl_hours = ttl_hours
        logger.info(f"Initialized AssetRegistry with TTL: {ttl_hours} hours")
    
    def register_asset(
        self,
        asset_url: str,
        workflow_id: str,
        prompt_id: str,
        mime_type: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bytes_size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssetRecord:
        """Register a new asset and return AssetRecord with asset_id"""
        # Generate asset_id (UUID-based for uniqueness)
        asset_id = str(uuid.uuid4())
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
        
        # Create record
        record = AssetRecord(
            asset_id=asset_id,
            asset_url=asset_url,
            mime_type=mime_type or "application/octet-stream",
            width=width,
            height=height,
            bytes_size=bytes_size or 0,
            sha256=None,  # Will be computed if needed
            created_at=datetime.now(),
            workflow_id=workflow_id,
            prompt_id=prompt_id,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._assets[asset_id] = record
        self._url_to_asset_id[asset_url] = asset_id
        
        logger.debug(f"Registered asset {asset_id} for workflow {workflow_id}")
        return record
    
    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        """Retrieve asset record by ID, checking expiration"""
        record = self._assets.get(asset_id)
        if not record:
            return None
        
        # Check expiration
        if record.expires_at and datetime.now() > record.expires_at:
            logger.debug(f"Asset {asset_id} has expired")
            del self._assets[asset_id]
            if record.asset_url in self._url_to_asset_id:
                del self._url_to_asset_id[record.asset_url]
            return None
        
        return record
    
    def cleanup_expired(self):
        """Remove expired assets from registry"""
        now = datetime.now()
        expired_ids = [
            asset_id for asset_id, record in self._assets.items()
            if record.expires_at and now > record.expires_at
        ]
        
        for asset_id in expired_ids:
            record = self._assets[asset_id]
            del self._assets[asset_id]
            if record.asset_url in self._url_to_asset_id:
                del self._url_to_asset_id[record.asset_url]
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired assets")
        
        return len(expired_ids)
    
    def get_asset_by_url(self, asset_url: str) -> Optional[AssetRecord]:
        """Get asset record by URL (for deduplication)"""
        asset_id = self._url_to_asset_id.get(asset_url)
        if asset_id:
            return self.get_asset(asset_id)
        return None
