"""
API Routes for TuningAI
Exposes all services as REST endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Optional
import os

from app.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ImprovementRequest,
    ImprovementResponse,
    RefinementRequest,
    RefinementResponse,
    InterviewQuestionsResponse,
    ATSCheckResponse
)
from app.services.analysis_service import get_analysis_service
from app.services.resume_service import get_resume_service
from app.services.job_service import get_job_service

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_resume(
    job_url: Optional[str] = Form(None),
    job_text: Optional[str] = Form(None),
    resume_file: UploadFile = File(None),
    resume_text: Optional[str] = Form(None)
):
    """
    Analyze resume against job description
    
    **Accepts:**
    - `job_url` OR `job_text` (job description)
    - `resume_file` OR `resume_text` (resume)
    
    **Returns:** Complete match analysis with scores, strengths, weaknesses
    """
    
    # Get services
    analysis_service = get_analysis_service()
    job_service = get_job_service()
    resume_service = get_resume_service()
    
    # 1. Get job description
    try:
        job_description = await job_service.get_job_description(
            job_url=job_url,
            job_text=job_text
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job description: {str(e)}"
        )
    
    # 2. Get resume text
    if resume_file and resume_file.filename:
        try:
            resume_content = await resume_service.parse_resume(
                resume_file.file,
                resume_file.filename
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume: {str(e)}"
            )
    elif resume_text:
        resume_content = resume_text
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either resume_file or resume_text"
        )
    
    # 3. Analyze match
    try:
        analysis = analysis_service.analyze_match(
            job_description,
            resume_content
        )
        
        return AnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/improve", response_model=ImprovementResponse, tags=["Optimization"])
async def generate_improvements(request: ImprovementRequest):
    """
    Generate specific resume improvements based on analysis
    
    **Requires:** Result from `/analyze` endpoint
    
    **Returns:** List of specific improvements with before/after text
    """
    
    analysis_service = get_analysis_service()
    
    try:
        improvements = analysis_service.generate_improvements(
            request.job_description,
            request.resume_text,
            request.analysis
        )
        
        return ImprovementResponse(**improvements)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Improvement generation failed: {str(e)}"
        )


@router.post("/refine", response_model=RefinementResponse, tags=["Interactive"])
async def refine_section(request: RefinementRequest):
    """
    Interactive refinement - user chats to improve specific sections
    
    **Use case:** User wants to tweak a specific section with natural language
    
    **Example:** "Make my Python experience sound more impressive"
    """
    
    analysis_service = get_analysis_service()
    
    try:
        refined_text = analysis_service.interactive_refinement(
            request.section_name,
            request.current_text,
            request.job_keywords,
            request.user_instruction
        )
        
        return RefinementResponse(
            refined_text=refined_text,
            section_name=request.section_name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refinement failed: {str(e)}"
        )


@router.post("/interview-questions", response_model=InterviewQuestionsResponse, tags=["Interview Prep"])
async def get_interview_questions(request: AnalysisRequest):
    """
    Predict likely interview questions based on job and resume
    
    **Returns:** 5-8 predicted questions with reasoning and suggested answers
    """
    
    analysis_service = get_analysis_service()
    
    try:
        # First analyze
        analysis = analysis_service.analyze_match(
            request.job_description,
            request.resume_text
        )
        
        # Then predict questions
        questions = analysis_service.predict_interview_questions(
            request.job_description,
            request.resume_text,
            analysis
        )
        
        return InterviewQuestionsResponse(**questions)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question prediction failed: {str(e)}"
        )


@router.post("/ats-check", response_model=ATSCheckResponse, tags=["ATS"])
async def check_ats(
    resume_file: UploadFile = File(None),
    resume_text: Optional[str] = Form(None)
):
    """
    Check ATS (Applicant Tracking System) compatibility
    
    **Shows:** What company robots actually see when parsing your resume
    
    **Returns:** Parsing issues, formatting problems, recommendations
    """
    
    analysis_service = get_analysis_service()
    resume_service = get_resume_service()
    
    # Get resume text
    if resume_file and resume_file.filename:
        try:
            resume_content = await resume_service.parse_resume(
                resume_file.file,
                resume_file.filename
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse resume: {str(e)}"
            )
    elif resume_text:
        resume_content = resume_text
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either resume_file or resume_text"
        )
    
    # Check ATS compatibility
    try:
        ats_check = analysis_service.check_ats_compatibility(resume_content)
        return ATSCheckResponse(**ats_check)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ATS check failed: {str(e)}"
        )


@router.post("/generate-resume", tags=["Export"])
async def generate_resume_file(request: ImprovementRequest):
    """
    Generate downloadable DOCX with improvements applied
    
    **Returns:** Download link for optimized resume
    """
    
    resume_service = get_resume_service()
    
    try:
        # Apply improvements
        improved_resume = resume_service.apply_improvements(
            request.resume_text,
            request.analysis.get('improvements', [])
        )
        
        # Generate DOCX
        docx_path = resume_service.generate_docx(improved_resume)
        
        return FileResponse(
            docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="resume_optimized.docx",
            headers={
                "Content-Disposition": "attachment; filename=resume_optimized.docx"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume generation failed: {str(e)}"
        )


# ===== INFO ENDPOINTS =====

@router.get("/features", tags=["Info"])
async def get_features():
    """
    List all available features
    
    **Use case:** Show what TuningAI can do
    """
    return {
        "phase_1_core": {
            "analyze": "Match resume to job with AI analysis",
            "improve": "Generate specific resume improvements",
            "refine": "Interactive section refinement via chat",
            "interview_questions": "Predict likely interview questions",
            "ats_check": "Check ATS compatibility",
            "generate_resume": "Export optimized resume as DOCX"
        },
        "phase_2_coming_soon": {
            "rag": "Semantic search across resume history",
            "company_intel": "Deep company research",
            "salary_insights": "Salary range predictions"
        },
        "phase_3_coming_soon": {
            "agents": "Multi-agent analysis system",
            "mock_interview": "AI mock interviews",
            "application_tracking": "Track all applications"
        }
    }


# ===== WEEK 2: RAG ENDPOINTS (stubs) =====

@router.post("/upload-resume-history", tags=["RAG - Coming Soon"])
async def upload_resume_history(file: UploadFile = File(...)):
    """
    Week 2: Upload past successful resumes to build knowledge base
    """
    raise HTTPException(
        status_code=501,
        detail="Coming in Week 2 - RAG feature"
    )


# ===== WEEK 3: AGENT ENDPOINTS (stubs) =====

@router.post("/analyze-with-agents", tags=["Agents - Coming Soon"])
async def analyze_with_agents(request: AnalysisRequest):
    """
    Week 3: Use multi-agent system for analysis
    """
    raise HTTPException(
        status_code=501,
        detail="Coming in Week 3 - Multi-agent feature"
    )