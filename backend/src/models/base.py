"""
Base models for Firestore documents
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime
# Removed DocumentReference import to fix OpenAPI schema generation

T = TypeVar('T')


class BaseFirestoreModel(BaseModel):
    """Base model for all Firestore documents"""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat() if dt else None
        }
    )
    
    id: Optional[str] = None  # Firestore document ID
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    last_updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    last_updated_by: Optional[str] = None


class UserReference(BaseModel):
    """User reference model"""
    uid: str
    email: str
    display_name: Optional[str] = None


class OrganizationReference(BaseModel):
    """Organization reference model (bank or client)"""
    id: str
    name: str
    type: str  # 'bank' or 'client'


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    errors: Optional[list[str]] = None


class PaginatedResponse(APIResponse[T]):
    """Paginated API response"""
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: Optional[bool] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None