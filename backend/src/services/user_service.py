"""
User service for managing user data and permissions
"""

from typing import Optional, List, Dict, Any
from google.cloud.firestore import DocumentReference, DocumentSnapshot
import logging

from config.firebase_config import get_firestore_client, get_user_by_uid
from models.user import User, UserProfile, UserCreate, UserUpdate, Role
from models.base import OrganizationReference

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    async def get_user_profile(self, uid: str) -> Optional[UserProfile]:
        """Get user profile by UID"""
        try:
            # Get user document from Firestore
            user_doc = self.db.collection('users').document(uid).get()
            
            if not user_doc.exists:
                logger.warning(f"User profile not found for UID: {uid}")
                return None
            
            user_data = user_doc.to_dict()
            
            # Get Firebase Auth user data
            try:
                auth_user = get_user_by_uid(uid)
            except:
                logger.warning(f"Firebase Auth user not found for UID: {uid}")
                auth_user = {'email_verified': False}
            
            # Get primary role name
            primary_role_name = None
            if user_data.get('primaryRole'):
                role_doc = user_data['primaryRole'].get()
                if role_doc.exists:
                    primary_role_name = role_doc.id
            
            # Get organization info
            organization = None
            if user_data.get('organizationId'):
                org_ref = user_data['organizationId']
                org_doc = org_ref.get()
                if org_doc.exists:
                    org_data = org_doc.to_dict()
                    organization = OrganizationReference(
                        id=org_doc.id,
                        name=org_data.get('name', ''),
                        type=user_data.get('organizationType', '')
                    )
            
            # Create user profile
            profile = UserProfile(
                uid=uid,
                email=user_data.get('email', ''),
                first_name=user_data.get('firstName', ''),
                last_name=user_data.get('lastName', ''),
                full_name=f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip(),
                primary_role=primary_role_name,
                organization=organization,
                language=user_data.get('language', 'es'),
                timezone=user_data.get('timezone', 'America/Santiago'),
                status=user_data.get('status', 'active'),
                email_verified=auth_user.get('email_verified', False),
                two_factor_enabled=user_data.get('twoFactorEnabled', False),
                last_login_at=user_data.get('loginMetadata', {}).get('lastLoginAt')
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile for {uid}: {e}")
            return None
    
    async def get_user_permissions(self, uid: str) -> List[str]:
        """Get user permissions from roles"""
        try:
            user_doc = self.db.collection('users').document(uid).get()
            
            if not user_doc.exists:
                return []
            
            user_data = user_doc.to_dict()
            permissions = set()
            
            # Get permissions from all roles
            roles = user_data.get('roles', [])
            if user_data.get('primaryRole'):
                roles.append(user_data['primaryRole'])
            
            for role_ref in roles:
                if isinstance(role_ref, DocumentReference):
                    role_doc = role_ref.get()
                    if role_doc.exists:
                        role_data = role_doc.to_dict()
                        role_permissions = role_data.get('permissions', [])
                        permissions.update(role_permissions)
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"Error getting user permissions for {uid}: {e}")
            return []
    
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user"""
        try:
            # Convert to User model
            user = User(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                language=user_data.language,
                timezone=user_data.timezone,
                organization_type=user_data.organization_type
            )
            
            # Set role reference
            if user_data.primary_role:
                role_ref = self.db.collection('roles').document(user_data.primary_role)
                user.primary_role = role_ref
                user.roles = [role_ref]
            
            # Set organization reference
            if user_data.organization_id and user_data.organization_type:
                if user_data.organization_type == 'bank':
                    org_ref = self.db.collection('banks').document(user_data.organization_id)
                elif user_data.organization_type == 'client':
                    org_ref = self.db.collection('clients').document(user_data.organization_id)
                else:
                    raise ValueError(f"Invalid organization type: {user_data.organization_type}")
                
                user.organization_id = org_ref
            
            # This would be called after Firebase Auth user creation
            # The UID would come from Firebase Auth
            # For now, returning the user object
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def update_user(self, uid: str, user_data: UserUpdate) -> Optional[UserProfile]:
        """Update user information"""
        try:
            user_ref = self.db.collection('users').document(uid)
            
            # Build update data
            update_data = {}
            if user_data.first_name is not None:
                update_data['first_name'] = user_data.first_name
            if user_data.last_name is not None:
                update_data['last_name'] = user_data.last_name
            if user_data.language is not None:
                update_data['language'] = user_data.language
            if user_data.timezone is not None:
                update_data['timezone'] = user_data.timezone
            if user_data.status is not None:
                update_data['status'] = user_data.status
            
            # Add timestamp
            from datetime import datetime
            update_data['last_updated_at'] = datetime.now()
            update_data['last_updated_by'] = user_ref  # Self-update
            
            # Update document
            user_ref.update(update_data)
            
            # Return updated profile
            return await self.get_user_profile(uid)
            
        except Exception as e:
            logger.error(f"Error updating user {uid}: {e}")
            return None
    
    async def get_roles(self) -> List[Role]:
        """Get all available roles"""
        try:
            roles_collection = self.db.collection('roles')
            docs = roles_collection.stream()
            
            roles = []
            for doc in docs:
                role_data = doc.to_dict()
                role = Role(
                    display_name=role_data.get('display_name', ''),
                    description=role_data.get('description', ''),
                    permissions=role_data.get('permissions', []),
                    created_at=role_data.get('created_at'),
                    last_updated_at=role_data.get('last_updated_at')
                )
                roles.append(role)
            
            return roles
            
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
    
    async def update_login_metadata(self, uid: str, ip_address: str):
        """Update user login metadata"""
        try:
            from datetime import datetime
            
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_data = user_doc.to_dict()
                login_metadata = current_data.get('loginMetadata', {})
                
                # Update login metadata
                login_metadata.update({
                    'lastLoginAt': datetime.now(),
                    'lastLoginIP': ip_address,
                    'loginCount': login_metadata.get('loginCount', 0) + 1
                })
                
                user_ref.update({
                    'loginMetadata': login_metadata,
                    'lastUpdatedAt': datetime.now()
                })
                
                logger.info(f"Updated login metadata for user {uid}")
            
        except Exception as e:
            logger.error(f"Error updating login metadata for {uid}: {e}")