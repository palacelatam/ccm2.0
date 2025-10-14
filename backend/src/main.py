"""
Client Confirmation Manager Backend API
FastAPI application with Firebase integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config.firebase_config import initialize_firebase
from config.settings import get_settings
from api.routes import auth, users, health, clients, banks, gmail, events, internal_tasks, sms
from api.middleware.auth_middleware import AuthMiddleware
from services.gmail_service import gmail_service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting CCM Backend API...")
    
    # Initialize Firebase
    initialize_firebase()
    print("✅ Firebase initialized")
    
    # Initialize Gmail service (optional - can also be done via endpoint)
    try:
        # Try to initialize Gmail service with either service account file or ADC
        await gmail_service.initialize()
        print("✅ Gmail service initialized")
        
        # Start Gmail monitoring automatically
        import asyncio
        monitoring_task = asyncio.create_task(
            gmail_service.start_monitoring(check_interval=30)
        )
        print("✅ Gmail monitoring started (30-second intervals)")
        
    except Exception as e:
        print(f"ℹ️  Gmail service not initialized: {e}")
        # Don't fail startup if Gmail isn't configured
    
    yield
    
    # Shutdown
    print("🛑 Shutting down CCM Backend API...")
    
    # Stop Gmail monitoring
    try:
        await gmail_service.stop_monitoring()
        print("✅ Gmail monitoring stopped")
    except Exception as e:
        print(f"ℹ️  Error stopping Gmail monitoring: {e}")


# Create FastAPI application
app = FastAPI(
    title="Client Confirmation Manager API",
    description="Backend API for Client Confirmation Manager - Multi-tenant SaaS platform for Chilean banking industry",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(clients.router, prefix="/api/v1", tags=["Clients"])
app.include_router(banks.router, prefix="/api/v1", tags=["Banks"])
app.include_router(gmail.router, prefix="/api/v1", tags=["Gmail"])
app.include_router(events.router, prefix="/api/v1", tags=["Events"])
app.include_router(internal_tasks.router, prefix="", tags=["Internal Tasks"])
app.include_router(sms.router)


# Root and health endpoints are handled by health.router


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False,
        log_level="info"
    )