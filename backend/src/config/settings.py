"""
Application settings and configuration
"""

from typing import Optional
import os


class Settings:
    """Application settings"""
    
    def __init__(self):
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # API Configuration
        self.api_title = "Client Confirmation Manager API"
        self.api_version = "2.0.0"
        
        # Firebase Configuration
        self.firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "ccm-dev-pool")
        self.firebase_emulator_host = os.getenv("FIREBASE_EMULATOR_HOST", "localhost")
        self.firebase_emulator_port = int(os.getenv("FIREBASE_EMULATOR_PORT", "8081"))
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # CORS
        self.allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        
        # Database
        self.use_firebase_emulator = os.getenv("USE_FIREBASE_EMULATOR", "true").lower() == "true"
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings