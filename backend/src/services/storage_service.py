"""
Google Cloud Storage service for handling settlement document uploads
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from config.storage_config import (
    get_storage_bucket, generate_storage_path, validate_file, 
    generate_signed_url, STORAGE_BUCKET_NAME
)

logger = logging.getLogger(__name__)

class StorageService:
    """Service for handling document uploads to Google Cloud Storage"""
    
    def __init__(self):
        try:
            self.bucket = get_storage_bucket()
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            raise Exception(f"Storage service initialization failed: {e}")
    
    async def upload_settlement_document(
        self, 
        file_content: bytes,
        filename: str,
        content_type: str,
        bank_id: str,
        segment_id: Optional[str] = None,
        uploaded_by: str = None
    ) -> Dict[str, Any]:
        """
        Upload settlement document to Cloud Storage
        
        Returns:
        {
            "success": bool,
            "storage_path": str,
            "public_url": str,
            "signed_url": str,
            "file_size": int,
            "content_type": str,
            "uploaded_at": str
        }
        """
        try:
            # Validate file
            is_valid, error_message = validate_file(file_content, filename, content_type)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_message
                }
            
            # Generate storage path
            storage_path = generate_storage_path(bank_id, segment_id, filename)
            
            # Create blob
            blob = self.bucket.blob(storage_path)
            
            # Set metadata
            blob.metadata = {
                "original_filename": filename,
                "bank_id": bank_id,
                "segment_id": segment_id or "default",
                "uploaded_by": uploaded_by or "system",
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_type": "settlement_document"
            }
            
            # Upload file
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            logger.info(f"Successfully uploaded document: {storage_path}")
            
            # Generate URLs
            public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{storage_path}"
            signed_url = generate_signed_url(storage_path, expiration_minutes=60)
            
            return {
                "success": True,
                "storage_path": storage_path,
                "public_url": public_url,
                "signed_url": signed_url,
                "file_size": len(file_content),
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading document {filename}: {e}")
            return {
                "success": False,
                "error": f"Failed to upload document: {str(e)}"
            }
    
    async def delete_settlement_document(self, storage_path: str) -> Dict[str, Any]:
        """
        Delete settlement document from Cloud Storage
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            # Delete file
            blob.delete()
            
            logger.info(f"Successfully deleted document: {storage_path}")
            
            return {
                "success": True,
                "message": "Document deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document {storage_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to delete document: {str(e)}"
            }
    
    async def get_document_info(self, storage_path: str) -> Dict[str, Any]:
        """
        Get information about a document in Cloud Storage
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if not blob.exists():
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            # Reload blob to get latest metadata
            blob.reload()
            
            return {
                "success": True,
                "storage_path": storage_path,
                "size": blob.size,
                "content_type": blob.content_type,
                "created_at": blob.time_created.isoformat() if blob.time_created else None,
                "updated_at": blob.updated.isoformat() if blob.updated else None,
                "metadata": blob.metadata or {},
                "public_url": f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{storage_path}",
                "signed_url": generate_signed_url(storage_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting document info for {storage_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to get document info: {str(e)}"
            }
    
    async def generate_document_signed_url(
        self, 
        storage_path: str, 
        expiration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Generate a new signed URL for document access
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if not blob.exists():
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            signed_url = generate_signed_url(storage_path, expiration_minutes)
            
            return {
                "success": True,
                "signed_url": signed_url,
                "expires_in_minutes": expiration_minutes
            }
            
        except Exception as e:
            logger.error(f"Error generating signed URL for {storage_path}: {e}")
            return {
                "success": False,
                "error": f"Failed to generate signed URL: {str(e)}"
            }