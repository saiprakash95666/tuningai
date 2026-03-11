"""
Analysis Service - Core business logic for resume-job matching
Orchestrates LLM, prompts, and other services
"""

from typing import Dict, Any, Optional
from app.llm.client import get_llm_client
from app.llm.prompts import get_prompts
from app.config import get_settings

settings = get_settings()


class AnalysisService:
    def __init__(self):
        self.llm = get_llm_client()
        self.prompts = get_prompts()
    
    def analyze_match(
        self,
        job_description: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Analyze how well resume matches job
        
        Returns:
            Complete analysis with all required fields
        """
    
        # Week 1: Direct LLM call
        if not settings.ENABLE_RAG:
            prompt = self.prompts.analyze_match(job_description, resume_text)
            
            response = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=self.prompts.SYSTEM_ANALYZER
            )
            
            # Validate and fix missing fields
            response = self._validate_analysis_response(response)
            
            return response
        
        # Week 2: Will add RAG logic here
        else:
            # TODO: Implement RAG-enhanced analysis
            pass

    def _validate_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate LLM response and add missing required fields
        """
    
        # Check recommendation section
        if "recommendation" in response:
            rec = response["recommendation"]
            
            # Add estimated_interview_probability if missing
            if "estimated_interview_probability" not in rec:
                # Calculate based on match_score
                score = response.get("match_score", 0)
                if score >= 85:
                    rec["estimated_interview_probability"] = "70%+"
                elif score >= 70:
                    rec["estimated_interview_probability"] = "50-70%"
                elif score >= 60:
                    rec["estimated_interview_probability"] = "30-50%"
                elif score >= 40:
                    rec["estimated_interview_probability"] = "10-30%"
                else:
                    rec["estimated_interview_probability"] = "<10%"
            
            # Add application_strategy if missing
            if "application_strategy" not in rec:
                verdict = response.get("verdict", "MAYBE")
                score = response.get("match_score", 0)
                
                if verdict == "APPLY" or score >= 75:
                    rec["application_strategy"] = (
                        "Apply soon while position is active. In your cover letter, "
                        "emphasize your matching skills and address any gaps by showing "
                        "willingness to learn. Consider reaching out to the hiring manager "
                        "on LinkedIn after applying."
                    )
                elif verdict == "MAYBE" or score >= 60:
                    rec["application_strategy"] = (
                        "Apply if you're willing to quickly learn the missing skills. "
                        "In your cover letter, directly address the gaps and highlight "
                        "your transferable experience. Focus on learning resources you're "
                        "already using for missing skills."
                    )
                else:
                    rec["application_strategy"] = (
                        "Consider building more experience before applying. Focus on roles "
                        "that better match your current skill set, or invest time in learning "
                        "the critical missing requirements before applying to similar positions."
                    )
        
        return response
    
    def generate_improvements(
        self,
        job_description: str,
        resume_text: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate specific improvements based on analysis
        
        Returns:
            {
                "improvements": [
                    {
                        "section": str,
                        "current": str,
                        "improved": str,
                        "reasoning": str,
                        "impact": str
                    }
                ],
                "summary": str
            }
        """
        
        weaknesses = analysis.get('weaknesses', [])
        
        prompt = self.prompts.generate_improvements(
            job_description,
            resume_text,
            weaknesses
        )
        
        response = self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_ANALYZER
        )
        
        return response
    
    def predict_interview_questions(
        self,
        job_description: str,
        resume_text: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likely interview questions
        
        Returns:
            {
                "questions": [
                    {
                        "question": str,
                        "reasoning": str,
                        "suggested_answer": str,
                        "priority": str
                    }
                ]
            }
        """
        
        weaknesses = analysis.get('weaknesses', [])
        
        prompt = self.prompts.predict_interview_questions(
            job_description,
            resume_text,
            weaknesses
        )
        
        response = self.llm.generate_structured(
            prompt=prompt,
            system_prompt="You are an experienced technical interviewer."
        )
        
        return response
    
    def check_ats_compatibility(
        self,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Check ATS compatibility
        
        Returns:
            {
                "ats_score": int,
                "parsed_correctly": [...],
                "parsing_failures": [...],
                "formatting_issues": [...],
                "recommendations": [...]
            }
        """
        
        prompt = self.prompts.check_ats_compatibility(resume_text)
        
        response = self.llm.generate_structured(
            prompt=prompt,
            system_prompt="You are an ATS parsing expert."
        )
        
        return response
    
    def interactive_refinement(
        self,
        section_name: str,
        current_text: str,
        job_keywords: list,
        user_instruction: str
    ) -> str:
        """
        Refine a specific section based on user chat
        Used for interactive editing
        """
        
        keywords_text = ", ".join(job_keywords)
        
        prompt = f"""Rewrite this resume section based on user's request.

**Section:** {section_name}

**Current text:**
{current_text}

**Keywords to incorporate:** {keywords_text}

**User's request:** {user_instruction}

**Requirements:**
- Maintain the same tone and style
- Add relevant keywords naturally
- Include metrics/numbers if possible
- Keep it truthful (don't fabricate experience)
- Make it ATS-friendly

**Output:** Just the improved text, no explanation."""
        
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_ANALYZER
        )
        
        return response.strip()
    
    # ===== WEEK 2: RAG METHODS (stubs) =====
    
    def _retrieve_similar_matches(self, job_description: str) -> str:
        """
        Week 2: Retrieve similar successful matches from vector DB
        """
        if not settings.ENABLE_RAG:
            return ""
        
        # TODO Week 2: Implement
        return ""
    
    # ===== WEEK 3: AGENT METHODS (stubs) =====
    
    def analyze_with_agents(
        self,
        job_description: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Week 3: Use multi-agent system
        """
        if not settings.ENABLE_AGENTS:
            return self.analyze_match(job_description, resume_text)
        
        # TODO Week 3: Implement
        return {}


# Singleton
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """Get analysis service instance"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service