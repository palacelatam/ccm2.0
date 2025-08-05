"""
Authentication middleware for verifying Firebase tokens
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import logging

from config.firebase_config import verify_firebase_token
from services.user_service import UserService
from models.user import AuthContext

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Firebase authentication"""
    
    # Routes that don't require authentication
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/verify",  # Auth verification endpoint
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware"""
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "Missing or invalid Authorization header",
                    "error_code": "MISSING_TOKEN"
                }
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify Firebase token
            decoded_token = verify_firebase_token(token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")
            
            # Get user profile and permissions
            user_service = UserService()
            user_profile = await user_service.get_user_profile(uid)
            
            if not user_profile:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "success": False,
                        "message": "User profile not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                )
            
            # Get user permissions
            permissions = await user_service.get_user_permissions(uid)
            
            # Create auth context
            auth_context = AuthContext(
                uid=uid,
                email=email,
                user_profile=user_profile,
                permissions=permissions,
                organization_id=user_profile.organization.id if user_profile.organization else None,
                organization_type=user_profile.organization.type if user_profile.organization else None
            )
            
            # Add auth context to request state
            request.state.auth = auth_context
            
            logger.info(f"Authenticated user: {email} ({uid})")
            
        except ValueError as e:
            logger.warning(f"Token verification failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "Invalid or expired token",
                    "error_code": "INVALID_TOKEN"
                }
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Authentication service error",
                    "error_code": "AUTH_SERVICE_ERROR"
                }
            )
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication"""
        # Exact match
        if path in self.EXCLUDED_PATHS:
            return True
        
        # Pattern matching for docs and OpenAPI
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            return True
        
        # Chrome dev tools path
        if path.startswith("/.well-known/"):
            return True
        
        return False


def get_auth_context(request: Request) -> AuthContext:
    """Get authentication context from request"""
    if not hasattr(request.state, "auth"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return request.state.auth


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in the function signature
            request = None
            
            # Check args for Request object
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Check kwargs for request
            if not request and 'request' in kwargs:
                request = kwargs['request']
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found in function parameters"
                )
            
            auth_context = get_auth_context(request)
            
            if not auth_context.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator