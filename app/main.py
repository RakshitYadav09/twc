"""
FastAPI main application entry point.
Configures the FastAPI app, routes, middleware, and lifecycle events.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.database.connection import DatabaseConnection
from app.routes import org_routes, auth_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Startup:
    - Connects to MongoDB
    - Initializes database connections
    
    Shutdown:
    - Closes MongoDB connection
    - Cleans up resources
    """
    # Startup
    print("🚀 Starting FastAPI application...")
    await DatabaseConnection.connect()
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down FastAPI application...")
    await DatabaseConnection.disconnect()
    print("✅ Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title="Multi-Tenant Organization Management API",
    description="""
    A production-ready FastAPI backend for managing organizations in a multi-tenant architecture.
    
    ## Features
    
    * **Multi-Tenant Architecture**: Each organization has its own MongoDB collection
    * **JWT Authentication**: Secure token-based authentication using JWT
    * **Password Hashing**: Bcrypt for secure password storage
    * **Async Operations**: Built with async/await for high performance
    * **Clean Architecture**: Modular design with services, repositories, and routes
    
    ## Authentication
    
    Most endpoints require authentication via JWT bearer token.
    
    1. First, create an organization or login via `/admin/login`
    2. Use the returned `access_token` in the Authorization header:
       `Authorization: Bearer <your_token_here>`
    
    ## Organization Collections
    
    Each organization gets its own collection named: `org_{organization_name}`
    
    Example: Organization "alpha" → Collection "org_alpha"
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_routes.router)
app.include_router(org_routes.router)


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint"
)
async def root():
    """
    Root endpoint providing API information.
    
    Returns basic API metadata and links to documentation.
    """
    return {
        "message": "Multi-Tenant Organization Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check"
)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns API health status and database connectivity.
    """
    try:
        # Check database connection
        db = DatabaseConnection.get_master_db()
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Logs the error and returns a standardized error response.
    """
    print(f"❌ Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "error": str(exc)
        }
    )


# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level="info"
    )
