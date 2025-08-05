"""
User management routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import List
import logging

from api.middleware.auth_middleware import get_auth_context, require_permission
from services.user_service import UserService
from models.base import APIResponse
from models.user import UserProfile, UserUpdate, Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=APIResponse[UserProfile])
async def get_my_profile(request: Request):
    """Get current user's profile"""
    auth_context = get_auth_context(request)
    
    if not auth_context.user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return APIResponse(
        success=True,
        data=auth_context.user_profile,
        message="Profile retrieved successfully"
    )


@router.put("/me", response_model=APIResponse[UserProfile])
async def update_my_profile(request: Request, user_data: UserUpdate):
    """Update current user's profile"""
    auth_context = get_auth_context(request)
    
    user_service = UserService()
    updated_profile = await user_service.update_user(auth_context.uid, user_data)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return APIResponse(
        success=True,
        data=updated_profile,
        message="Profile updated successfully"
    )


@router.get("/{user_uid}", response_model=APIResponse[UserProfile])
@require_permission("view_users")
async def get_user_profile(request: Request, user_uid: str):
    """Get user profile by UID (requires view_users permission)"""
    auth_context = get_auth_context(request)
    
    # Additional authorization: users can only view users in their organization
    user_service = UserService()
    target_profile = await user_service.get_user_profile(user_uid)
    
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user can access this profile
    if not auth_context.can_access_organization(
        target_profile.organization.id if target_profile.organization else "",
        target_profile.organization.type if target_profile.organization else ""
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user's profile"
        )
    
    return APIResponse(
        success=True,
        data=target_profile,
        message="User profile retrieved successfully"
    )


@router.put("/{user_uid}", response_model=APIResponse[UserProfile])
@require_permission("manage_users")
async def update_user_profile(request: Request, user_uid: str, user_data: UserUpdate):
    """Update user profile by UID (requires manage_users permission)"""
    auth_context = get_auth_context(request)
    
    # Additional authorization check
    user_service = UserService()
    target_profile = await user_service.get_user_profile(user_uid)
    
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not auth_context.can_access_organization(
        target_profile.organization.id if target_profile.organization else "",
        target_profile.organization.type if target_profile.organization else ""
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this user"
        )
    
    updated_profile = await user_service.update_user(user_uid, user_data)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user profile"
        )
    
    return APIResponse(
        success=True,
        data=updated_profile,
        message="User profile updated successfully"
    )


@router.get("/", response_model=APIResponse[List[UserProfile]])
@require_permission("view_users")
async def list_users(request: Request):
    """List users in organization (requires view_users permission)"""
    auth_context = get_auth_context(request)
    
    # This would need to be implemented in UserService
    # For now, return empty list with TODO message
    return APIResponse(
        success=True,
        data=[],
        message="User listing not yet implemented - requires organization-based filtering"
    )


@router.get("/roles/available", response_model=APIResponse[List[Role]])
async def get_available_roles(request: Request):
    """Get available roles for user assignment"""
    auth_context = get_auth_context(request)
    
    user_service = UserService()
    roles = await user_service.get_roles()
    
    return APIResponse(
        success=True,
        data=roles,
        message="Available roles retrieved successfully"
    )