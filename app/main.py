"""Main FastAPI application."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1 import devices_router, health_router
from app.schemas import ErrorResponse, ErrorDetail
from app.config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AAC IoT Hub",
    description="Local IoT device control hub - REST API for Yeelight and more",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow all origins for local network use
# TODO: Configure allowed origins for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (local network)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Exception handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with ErrorResponse format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code=f"HTTP_{exc.status_code}",
                message=exc.detail,
            )
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details={"error": str(exc)}
            )
        ).model_dump()
    )


# Register routers
app.include_router(devices_router)
app.include_router(health_router)


# Favicon endpoint (suppress browser 404 logs)
@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests."""
    from fastapi.responses import Response
    return Response(status_code=204)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - basic API info."""
    return {
        "name": "AAC IoT Hub",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1/devices",
    }