"""
Google Cloud Storage configuration for settlement document uploads
"""

import os
from google.cloud import storage
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_PROJECT_ID = "ccm-dev-pool"
STORAGE_BUCKET_NAME = "ccm-dev-pool-settlement-documents"
STORAGE_LOCATION = "southamerica-west1"  # Santiago region

# File upload constraints
MAX_FILE_SIZE_MB = 10  # 10MB max file size
ALLOWED_CONTENT_TYPES = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
ALLOWED_EXTENSIONS = [".docx"]

def get_storage_client():
    """
    Get Google Cloud Storage client
    Uses Application Default Credentials or service account if configured
    """
    try:
        # Check if we're running in development mode with emulator
        storage_emulator_host = os.getenv('STORAGE_EMULATOR_HOST')
        if storage_emulator_host:
            logger.info(f"Using Storage Emulator at {storage_emulator_host}")
            client = storage.Client(project=STORAGE_PROJECT_ID)
            return client
        
        # For production/development, try service account first, then ADC
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if service_account_path and os.path.exists(service_account_path):
            logger.info(f"Using service account from {service_account_path}")
            credentials = service_account.Credentials.from_service_account_file(service_account_path)
            client = storage.Client(credentials=credentials, project=STORAGE_PROJECT_ID)
        else:
            # Try to use ADC, but provide better error handling
            try:
                logger.info("Attempting to use Application Default Credentials")
                client = storage.Client(project=STORAGE_PROJECT_ID)
                # Test the client to make sure authentication works
                try:
                    list(client.list_buckets(max_results=1))
                except Exception as auth_test_error:
                    raise Exception(f"Authentication test failed: {auth_test_error}. Please run 'gcloud auth application-default login' or set up a service account key.")
            except Exception as adc_error:
                raise Exception(f"Failed to authenticate with ADC: {adc_error}. Please run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS environment variable to a service account key file.")
        
        logger.info(f"Storage client initialized for project: {STORAGE_PROJECT_ID}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize storage client: {e}")
        raise

def get_storage_bucket():
    """Get the storage bucket instance"""
    client = get_storage_client()
    return client.bucket(STORAGE_BUCKET_NAME)

def generate_storage_path(bank_id: str, segment_id: str, filename: str, unique_suffix: str = None) -> str:
    """
    Generate standardized storage path for settlement documents
    Format: {bank-id}/{segment-id}/{filename}_{timestamp}_{unique-suffix}.pdf
    """
    import datetime
    
    # Clean filename (remove extension)
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate unique suffix if not provided
    if not unique_suffix:
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
    
    # Build filename
    final_filename = f"{name_without_ext}_{timestamp}_{unique_suffix}.docx"
    
    # Build full path
    return f"{bank_id}/{segment_id or 'default'}/{final_filename}"

def validate_file(file_content: bytes, filename: str, content_type: str) -> tuple[bool, str]:
    """
    Validate uploaded file for security and constraints
    Returns (is_valid, error_message)
    """
    # Check file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB}MB)"
    
    # Check content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        return False, f"Content type '{content_type}' not allowed. Only Word documents are permitted."
    
    # Check file extension
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return False, f"File extension not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files are permitted."
    
    # Basic DOCX signature check (DOCX files start with PK as they are ZIP archives)
    if not file_content.startswith(b'PK'):
        return False, "Invalid Word document format"
    
    return True, ""

def generate_signed_url(storage_path: str, expiration_minutes: int = 60) -> str:
    """
    Generate a signed URL for secure document access using storage service account
    Default expiration: 1 hour
    """
    try:
        from google.auth import impersonated_credentials
        from google.auth import default
        from datetime import datetime, timedelta
        
        # Get default credentials (ADC)
        source_credentials, _ = default()
        
        # Create impersonated credentials for the storage service account
        target_service_account = "ccm-storage-service@ccm-dev-pool.iam.gserviceaccount.com"
        target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        
        impersonated_creds = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_service_account,
            target_scopes=target_scopes
        )
        
        # Create storage client with impersonated credentials
        client = storage.Client(credentials=impersonated_creds, project=STORAGE_PROJECT_ID)
        bucket = client.bucket(STORAGE_BUCKET_NAME)
        blob = bucket.blob(storage_path)
        
        # Generate signed URL with expiration
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
        signed_url = blob.generate_signed_url(
            expiration=expiration,
            method='GET',
            version='v4'
        )
        
        return signed_url
        
    except Exception as e:
        logger.error(f"Failed to generate signed URL for {storage_path}: {e}")
        raise