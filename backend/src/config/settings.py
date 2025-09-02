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
        
        # Database Configuration
        self.use_firebase_emulator = os.getenv("USE_FIREBASE_EMULATOR", "false").lower() == "true"
        self.use_cmek_database = os.getenv("USE_CMEK_DATABASE", "true").lower() == "true"
        self.firebase_database_id = os.getenv("FIREBASE_DATABASE_ID", "ccm-development")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # LLM Configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic")  # anthropic, vertex, openai
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        
        # GCP Vertex AI (for future use)
        self.vertex_project_id = os.getenv("VERTEX_PROJECT_ID", self.firebase_project_id)
        self.vertex_location = os.getenv("VERTEX_LOCATION", "us-central1")
        self.vertex_model = os.getenv("VERTEX_MODEL", "claude-3-5-sonnet@20241022")
        
        # Twilio SMS Configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.sms_rate_limit_per_minute = int(os.getenv("SMS_RATE_LIMIT_PER_MINUTE", "10"))
        self.sms_daily_limit_default = int(os.getenv("SMS_DAILY_LIMIT_DEFAULT", "100"))


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings