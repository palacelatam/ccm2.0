"""
User models matching Firestore schema
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
# Removed DocumentReference import to fix OpenAPI schema generation

from .base import BaseFirestoreModel, UserReference, OrganizationReference


class LoginMetadata(BaseModel):
    """User login tracking metadata"""
    last_login_at: Optional[datetime] = Field(None, alias="lastLoginAt")
    last_login_ip: Optional[str] = Field(None, alias="lastLoginIP")
    login_count: int = Field(0, alias="loginCount")
    
    class Config:
        populate_by_name = True


class Role(BaseFirestoreModel):
    """Role model"""
    display_name: str
    description: str
    permissions: List[str] = Field(default_factory=list)


class User(BaseFirestoreModel):
    """User model matching Firestore users collection"""
    
    # Personal Information
    first_name: str
    last_name: str
    email: EmailStr
    
    # Role and Organization (using strings instead of DocumentReference for API compatibility)
    roles: List[str] = Field(default_factory=list)
    primary_role: Optional[str] = None
    organization_id: Optional[str] = None
    organization_type: Optional[str] = None  # 'bank' or 'client'
    
    # Preferences
    language: str = "es"
    timezone: str = "America/Santiago"
    
    # Metadata
    login_metadata: LoginMetadata = Field(default_factory=LoginMetadata)
    status: str = "active"  # active, inactive, pending, suspended
    email_verified: bool = False
    two_factor_enabled: bool = False
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == "active"


class UserProfile(BaseModel):
    """User profile response model"""
    uid: str
    email: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    full_name: str = Field(alias="fullName")
    primary_role: Optional[str] = Field(None, alias="primaryRole")
    organization: Optional[OrganizationReference] = None
    language: str
    timezone: str
    status: str
    email_verified: bool = Field(alias="emailVerified")
    two_factor_enabled: bool = Field(alias="twoFactorEnabled")
    last_login_at: Optional[datetime] = Field(None, alias="lastLoginAt")
    
    class Config:
        populate_by_name = True  # Allow both field name and alias


class UserCreate(BaseModel):
    """Model for creating a new user"""
    email: EmailStr
    first_name: str
    last_name: str
    primary_role: str
    organization_id: Optional[str] = None
    organization_type: Optional[str] = None
    language: str = "es"
    timezone: str = "America/Santiago"


class UserUpdate(BaseModel):
    """Model for updating user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None


class AuthContext(BaseModel):
    """Authentication context for requests"""
    uid: str
    email: str
    user_profile: Optional[UserProfile] = None
    permissions: List[str] = Field(default_factory=list)
    organization_id: Optional[str] = None
    organization_type: Optional[str] = None
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def is_bank_admin(self) -> bool:
        """Check if user is a bank admin"""
        return self.organization_type == "bank" and "manage_client_segments" in self.permissions
    
    def is_client_admin(self) -> bool:
        """Check if user is a client admin"""
        return self.organization_type == "client" and "manage_settings" in self.permissions
    
    def can_access_organization(self, org_id: str, org_type: str) -> bool:
        """Check if user can access specific organization"""
        if self.organization_type == "bank" and org_type == "bank":
            return self.organization_id == org_id
        elif self.organization_type == "client" and org_type == "client":
            return self.organization_id == org_id
        elif self.organization_type == "bank" and org_type == "client":
            # Bank admins can access their clients (would need additional logic)
            return True
        return False