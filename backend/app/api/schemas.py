"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ===== REQUEST SCHEMAS =====

class AnalysisRequest(BaseModel):
    """Request for analyzing resume-job match"""
    job_description: str = Field(..., description="Job description text")
    resume_text: str = Field(..., description="Resume text content")


class ImprovementRequest(BaseModel):
    """Request for generating improvements"""
    job_description: str
    resume_text: str
    analysis: Dict[str, Any] = Field(..., description="Analysis result from /analyze")


class RefinementRequest(BaseModel):
    """Request for interactive refinement"""
    section_name: str = Field(..., description="Resume section to refine")
    current_text: str = Field(..., description="Current section text")
    job_keywords: List[str] = Field(..., description="Keywords from job")
    user_instruction: str = Field(..., description="User's refinement request")


# ===== RESPONSE SCHEMAS =====

class Strength(BaseModel):
    """A strength in the resume"""
    point: str
    evidence: str
    importance: str = Field(..., pattern="^(high|medium|low)$")


class Weakness(BaseModel):
    """A weakness/gap in the resume"""
    point: str
    missing_keyword: Optional[str] = None
    severity: str = Field(..., pattern="^(critical|moderate|minor)$")


class ATSCompatibility(BaseModel):
    """ATS parsing compatibility"""
    score: int = Field(..., ge=0, le=100)
    issues: List[str]


class Recommendation(BaseModel):
    """Application recommendation"""
    should_apply: bool
    reasoning: str
    priority: str = Field(..., pattern="^(high|medium|low)$")
    estimated_interview_probability: Optional[str] = Field(
        None, 
        pattern="^(<10%|10-30%|30-50%|50-70%|70%\+)$",
        description="Estimated interview probability range"
    )
    application_strategy: Optional[str] = Field(
        None,
        description="Specific advice on how to apply (cover letter tips, etc.)"
    )


class AnalysisResponse(BaseModel):
    """Response from /analyze endpoint"""
    match_score: int = Field(..., ge=0, le=100)
    verdict: str = Field(..., pattern="^(APPLY|DON'T APPLY|MAYBE)$")
    confidence: float = Field(..., ge=0, le=1)
    strengths: List[Strength]
    weaknesses: List[Weakness]
    ats_compatibility: ATSCompatibility
    recommendation: Recommendation


class Improvement(BaseModel):
    """A specific improvement suggestion"""
    section: str
    current: str
    improved: str
    reasoning: str
    impact: str = Field(..., pattern="^(high|medium|low)$")


class ImprovementResponse(BaseModel):
    """Response from /improve endpoint"""
    improvements: List[Improvement]
    summary: str


class RefinementResponse(BaseModel):
    """Response from /refine endpoint"""
    refined_text: str
    section_name: str


class InterviewQuestion(BaseModel):
    """A predicted interview question"""
    question: str
    reasoning: str
    suggested_answer: str
    priority: str = Field(..., pattern="^(high|medium|low)$")


class InterviewQuestionsResponse(BaseModel):
    """Response from /interview-questions endpoint"""
    questions: List[InterviewQuestion]


class ATSCheckResponse(BaseModel):
    """Response from /ats-check endpoint"""
    ats_score: int = Field(..., ge=0, le=100)
    parsed_correctly: List[str]
    parsing_failures: List[Dict[str, str]]
    formatting_issues: List[str]
    recommendations: List[str]


# ===== WEEK 2: RAG SCHEMAS (not used yet) =====

class RAGSearchRequest(BaseModel):
    """Week 2: RAG search request"""
    query: str
    k: int = Field(default=5, ge=1, le=20)


# ===== WEEK 3: AGENT SCHEMAS (not used yet) =====

class AgentExecutionResponse(BaseModel):
    """Week 3: Agent execution response"""
    result: Dict[str, Any]
    agent_trace: List[Dict[str, Any]]
    execution_time: float