"""
Authentication routes for Firebase token verification
"""

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
import logging

from api.middleware.auth_middleware import get_auth_context
from services.user_service import UserService
from models.base import APIResponse
from models.user import UserProfile, AuthContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class TokenVerifyRequest(BaseModel):
    """Request model for token verification"""
    token: str


class TokenVerifyResponse(BaseModel):
    """Response model for token verification"""
    success: bool
    user_profile: UserProfile
    permissions: list[str]


@router.post("/verify")
async def verify_token(request: TokenVerifyRequest):
    """
    Verify Firebase token and return user profile
    This endpoint doesn't use auth middleware since it's the verification endpoint
    """
    try:
        from config.firebase_config import verify_firebase_token
        
        # Verify Firebase token
        decoded_token = verify_firebase_token(request.token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email", "")
        
        # Get user profile and permissions
        user_service = UserService()
        user_profile = await user_service.get_user_profile(uid)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        permissions = await user_service.get_user_permissions(uid)
        
        # Update login metadata
        await user_service.update_login_metadata(uid, "127.0.0.1")  # Local dev IP
        
        response_data = TokenVerifyResponse(
            success=True,
            user_profile=user_profile,
            permissions=permissions
        )
        
        return {
            "success": True,
            "data": {
                "success": True,
                "user_profile": user_profile.dict(),
                "permissions": permissions
            },
            "message": "Token verified successfully"
        }
        
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.get("/profile")
async def get_current_user_profile(request: Request):
    """Get current authenticated user's profile"""
    auth_context = get_auth_context(request)
    
    if not auth_context.user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return {
        "success": True,
        "data": auth_context.user_profile.dict(),
        "message": "User profile retrieved successfully"
    }


@router.get("/permissions")
async def get_current_user_permissions(request: Request):
    """Get current authenticated user's permissions"""
    auth_context = get_auth_context(request)
    
    return {
        "success": True,
        "data": auth_context.permissions,
        "message": "User permissions retrieved successfully"
    }


@router.get("/context")
async def get_auth_context_endpoint(request: Request):
    """Get full authentication context for debugging"""
    auth_context = get_auth_context(request)
    
    return {
        "success": True,
        "data": auth_context.dict(),
        "message": "Authentication context retrieved successfully"
    }