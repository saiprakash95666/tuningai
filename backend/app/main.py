"""
TuningAI - AI-Powered Resume Optimization
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import routes

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
    allow_origins=["*"],  # In production: specify domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api/v1", tags=["TuningAI"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": "TuningAI",
        "tagline": "Tune your resume, land the right job",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "api": "/api/v1",
        "phase": "Week 1: Core Resume Tuning",
        "features": {
            "analyze": "✅ Match resume to job",
            "improve": "✅ Generate improvements",
            "ats_check": "✅ ATS compatibility",
            "interview_prep": "✅ Predict questions",
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
        "version": "0.1.0",
        "rag_enabled": settings.ENABLE_RAG,
        "agents_enabled": settings.ENABLE_AGENTS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )