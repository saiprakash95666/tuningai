"""
TuningAI - AI-Powered Resume Optimization
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="TuningAI",
    description="Tune your resume for any job with AI - Focus on quality, not quantity",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes will be added here as we build them
# from app.api import routes
# app.include_router(routes.router, prefix="/api/v1", tags=["tuning"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": "TuningAI",
        "tagline": "Tune your resume, land the right job",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "phase": "Week 1: Core Resume Tuning",
        "features": {
            "rag": settings.ENABLE_RAG,
            "agents": settings.ENABLE_AGENTS
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "TuningAI",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )