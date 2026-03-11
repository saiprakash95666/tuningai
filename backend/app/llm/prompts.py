"""
Prompt templates for TuningAI
Real-world quality prompts for professional resume optimization.
"""

from typing import Dict, Any, List


class PromptTemplates:
    """Professional-grade prompt templates"""
    
    # ===== SYSTEM PROMPTS =====
    
    SYSTEM_ANALYZER = """You are an elite resume optimization expert with deep knowledge of:

**ATS Systems:**
- How major ATS platforms parse resumes (Greenhouse, Lever, Workday, Taleo)
- Common parsing failures and how to avoid them
- Keyword matching algorithms and semantic analysis
- Resume ranking factors used by recruiters

**Recruiting Industry:**
- What hiring managers actually look for in resumes
- Industry-specific terminology and expectations
- Red flags that get resumes rejected
- Green flags that get interviews scheduled

**Your Approach:**
- Data-driven: Base recommendations on actual job requirements
- Specific: Provide actionable improvements with exact wording
- Honest: Never suggest lying or exaggerating experience
- Strategic: Focus on high-impact changes that increase interview probability

**Your Analysis Style:**
- Be direct and clear - no corporate jargon
- Quantify everything when possible (scores, percentages, counts)
- Cite evidence from the resume and job description
- Explain WHY each recommendation matters"""

    # ===== CORE ANALYSIS PROMPTS =====
    
    @staticmethod
    def analyze_match(job_description: str, resume_text: str) -> str:
        """Enhanced match analysis prompt"""
        return f"""You are analyzing a resume against a job description. Provide a comprehensive, actionable analysis.

**JOB DESCRIPTION:**
{job_description}

**CANDIDATE'S RESUME:**
{resume_text}

Analyze this match systematically and return ONLY valid JSON in this EXACT format:

{{
  "match_score": <integer 0-100>,
  "verdict": "<APPLY|DON'T APPLY|MAYBE>",
  "confidence": <float 0.0-1.0>,
  
  "strengths": [
    {{
      "point": "Clear, specific strength (e.g., 'Has 7 years Python experience, exceeds 5+ requirement')",
      "evidence": "Exact quote from resume that proves this",
      "importance": "high|medium|low"
    }}
  ],
  
  "weaknesses": [
    {{
      "point": "Specific gap (e.g., 'No Kubernetes mentioned, appears 8 times in job description')",
      "missing_keyword": "Exact keyword/skill missing",
      "severity": "critical|moderate|minor"
    }}
  ],
  
  "ats_compatibility": {{
    "score": <integer 0-100>,
    "issues": [
      "Specific ATS parsing issues (e.g., 'Header/footer text will be ignored', 'Two-column layout confuses parsers')"
    ]
  }},
  
  "recommendation": {{
    "should_apply": <boolean>,
    "reasoning": "Specific, data-driven explanation with strategic advice",
    "priority": "high|medium|low",
    "estimated_interview_probability": "<REQUIRED - MUST BE ONE OF: <10%|10-30%|30-50%|50-70%|70%+>",
    "application_strategy": "Specific tactical advice: when to apply, cover letter focus points, how to position gaps, networking suggestions"
  }}
}}

**CRITICAL - RECOMMENDATION SECTION REQUIREMENTS:**

You MUST include ALL these fields in recommendation:

1. **should_apply** (boolean):
   - true if match_score >= 60 and no critical dealbreakers
   - false if match_score < 60 or has critical dealbreakers

2. **reasoning** (string):
   - Explain the verdict with data
   - Reference specific match metrics
   - Be honest about gaps

3. **priority** (string):
   - "high" = 75+ match score, apply immediately
   - "medium" = 60-74 match score, apply this week
   - "low" = 50-59 match score, apply if no better options

4. **estimated_interview_probability** (string) - REQUIRED:
   - "<10%" = Very unlikely (match_score 0-40, missing critical skills)
   - "10-30%" = Unlikely (match_score 41-60, missing multiple requirements)
   - "30-50%" = Possible (match_score 61-70, some gaps but learnable)
   - "50-70%" = Likely (match_score 71-85, strong match)
   - "70%+" = Very likely (match_score 86-100, excellent match)
   
   Base this on:
   - Match score
   - Number of critical gaps
   - Competition level (infer from seniority)
   - Industry standard interview rates

5. **application_strategy** (string) - REQUIRED:
   Provide 2-3 specific tactical recommendations:
   
   For APPLY verdict:
   - "Apply within 48 hours to be early applicant"
   - "In cover letter, emphasize your [strength] and mention you're actively learning [gap]"
   - "Reach out to hiring manager on LinkedIn after applying"
   - "Highlight [specific project] that matches their [requirement]"
   
   For MAYBE verdict:
   - "Apply only if willing to quickly learn [critical gap]"
   - "In cover letter, address the Kubernetes gap by highlighting Docker experience"
   - "Consider getting [certification] before applying to strengthen candidacy"
   
   For DON'T APPLY verdict:
   - "Missing too many critical requirements - focus on roles requiring [your strengths]"
   - "Consider applying for mid-level version of this role instead"
   - "Gain [skill] experience before applying to senior positions"

**EXAMPLE COMPLETE RECOMMENDATION:**

{{
  "recommendation": {{
    "should_apply": true,
    "reasoning": "Strong match on 7/10 required skills (70% match). Missing Kubernetes and FastAPI are learnable. Flask experience transfers well to FastAPI. 6 years experience exceeds 5+ requirement. AWS and PostgreSQL experience are solid matches.",
    "priority": "medium",
    "estimated_interview_probability": "30-50%",
    "application_strategy": "Apply this week while position is fresh. In cover letter: (1) Emphasize 6 years Python experience and 50K user scale, (2) Mention you're learning FastAPI (similar to Flask), (3) Highlight AWS deployment experience. Consider reaching out to engineering manager on LinkedIn after applying to stand out from other candidates."
  }}
}}

**SCORING CRITERIA:**
- **Match Score Calculation:**
  - Required skills match: 50% weight (count how many they have vs need)
  - Experience level match: 20% weight (years, seniority)
  - Industry/domain match: 15% weight (similar companies, projects)
  - Education match: 10% weight
  - Cultural/soft skills match: 5% weight

- **Verdict Guidelines:**
  - APPLY: 75+ score, has 80%+ of required skills, missing skills are learnable
  - MAYBE: 60-74 score, has 60-79% of required skills, some critical gaps
  - DON'T APPLY: <60 score, missing 40%+ of required skills, or missing critical must-haves

**ANALYSIS REQUIREMENTS:**
1. **Strengths (3-5 items):**
   - Quote exact phrases from resume as evidence
   - Explain why each matters for THIS job
   - Prioritize by importance (high = core requirements, medium = preferred, low = nice-to-have)

2. **Weaknesses (2-5 items):**
   - Count keyword frequency in JD (e.g., "Docker mentioned 5 times")
   - Mark severity: critical = must-have skill missing, moderate = preferred skill missing, minor = nice-to-have missing
   - Be specific about what's missing

3. **ATS Compatibility:**
   - Check for: headers/footers, tables, columns, graphics, special characters, non-standard fonts
   - Score: 90-100 = excellent, 70-89 = good, 50-69 = needs work, <50 = major issues

**IMPORTANT:**
- Base everything on actual content - don't assume or hallucinate
- Count actual keyword occurrences
- Be specific with evidence
- ALL fields in recommendation are REQUIRED - do not omit any
- Output ONLY the JSON, no other text
- Do not add any fields not specified in the schema"""

    @staticmethod
    def generate_improvements(
        job_description: str,
        resume_text: str,
        weaknesses: List[Dict[str, Any]]
    ) -> str:
        """Enhanced improvement generation prompt"""
        
        weakness_details = []
        for w in weaknesses:
            weakness_details.append(
                f"- {w['point']} "
                f"(Missing: {w.get('missing_keyword', 'N/A')}, "
                f"Severity: {w.get('severity', 'unknown')})"
            )
        weaknesses_text = "\n".join(weakness_details)
        
        return f"""Generate specific, actionable resume improvements to address the identified gaps.

**JOB DESCRIPTION:**
{job_description}

**CURRENT RESUME:**
{resume_text}

**GAPS TO ADDRESS:**
{weaknesses_text}

Return improvements in this EXACT JSON format:

{{
  "improvements": [
    {{
      "section": "Specific section (e.g., 'Skills', 'Experience - Software Engineer at Google', 'Summary')",
      "current": "Current text from resume OR 'MISSING' if section doesn't exist",
      "improved": "Complete improved text - ready to copy/paste",
      "reasoning": "Why this helps (be specific - reference job requirements)",
      "impact": "high|medium|low",
      "keywords_added": ["list", "of", "keywords", "naturally", "incorporated"]
    }}
  ],
  "summary": "Overall strategy and approach for these improvements"
}}

**IMPROVEMENT GUIDELINES:**

1. **Add Missing Keywords Naturally:**
   - Don't just list keywords - weave them into accomplishments
   - Bad: "Skills: Python, Docker, Kubernetes"
   - Good: "Built microservices with Python and FastAPI, containerized with Docker, deployed on Kubernetes clusters handling 10K+ requests/second"

2. **Quantify Everything:**
   - Add metrics, percentages, scale, impact
   - Bad: "Improved application performance"
   - Good: "Optimized Python application, reducing API response time by 60% (800ms → 320ms) and cutting infrastructure costs by $40K/year"

3. **Use Action Verbs:**
   - Led, Built, Designed, Optimized, Scaled, Architected, Implemented
   - Avoid: Responsible for, Worked on, Helped with

4. **Match Job Description Tone:**
   - If JD says "built scalable systems" → use "scalable" in resume
   - If JD emphasizes "team collaboration" → highlight team projects
   - Mirror their language but don't plagiarize

5. **ATS Optimization:**
   - Use standard section headers (Experience, Education, Skills)
   - Avoid tables, text boxes, headers/footers
   - Use simple bullet points (• or -)
   - Include both acronyms and full terms (e.g., "AWS (Amazon Web Services)")

6. **Truthfulness is CRITICAL:**
   - Only suggest adding skills they likely have or can quickly learn
   - Never fabricate job titles, companies, or achievements
   - If suggesting a new skill, note: "Add if you have experience with this"

**PRIORITY SYSTEM:**
- **High impact:** Addresses critical missing skills (severity: critical)
- **Medium impact:** Addresses preferred skills (severity: moderate)  
- **Low impact:** Polish and optimization (severity: minor)

**EXAMPLE HIGH-QUALITY IMPROVEMENT:**

Section: Experience - Senior Developer at TechCorp
Current: "Built web applications using Python and Flask"
Improved: "Architected and deployed 5 production microservices using Python/FastAPI, serving 2M+ daily users with 99.9% uptime. Implemented Docker containerization and CI/CD pipelines, reducing deployment time from 2 hours to 15 minutes."
Reasoning: Adds missing FastAPI keyword (mentioned 6x in JD), includes Docker (critical requirement), quantifies scale and impact, uses strong action verb "Architected"
Impact: high
Keywords added: ["FastAPI", "microservices", "Docker", "CI/CD", "99.9% uptime"]

Return ONLY valid JSON, no other text."""

    @staticmethod
    def predict_interview_questions(
        job_description: str,
        resume_text: str,
        weaknesses: List[Dict[str, Any]]
    ) -> str:
        """Enhanced interview question prediction"""
        
        weakness_points = [f"- {w['point']}" for w in weaknesses[:5]]
        gaps_text = "\n".join(weakness_points)
        
        return f"""Based on this job and resume, predict the most likely interview questions with strategic answers.

**JOB DESCRIPTION:**
{job_description[:2000]}...

**CANDIDATE'S RESUME:**
{resume_text[:2000]}...

**IDENTIFIED GAPS:**
{gaps_text}

Return predictions in this EXACT JSON format:

{{
  "questions": [
    {{
      "question": "The exact question they'll ask",
      "reasoning": "Why they'll ask this (based on JD requirements or resume gaps)",
      "suggested_answer": "Strategic answer framework using STAR method where relevant",
      "priority": "high|medium|low",
      "question_type": "technical|behavioral|situational|gap_probing"
    }}
  ]
}}

**QUESTION PREDICTION STRATEGY:**

1. **Gap-Based Questions (HIGHEST PRIORITY):**
   - They WILL ask about missing critical skills
   - Example: If resume lacks Kubernetes but JD requires it:
     - Question: "I see you don't have Kubernetes experience. How would you handle our K8s deployments?"
     - Suggested answer: "While I haven't used Kubernetes in production yet, I have extensive Docker experience and have been studying K8s through [specific learning]. In my current role, I've managed containerized deployments at scale using [actual tool], which gave me strong foundations in container orchestration concepts. I'm confident I could get up to speed quickly."

2. **Experience Verification Questions:**
   - They'll deep-dive on resume claims
   - Example: If resume says "scaled system to 1M users":
     - Question: "Tell me about a time you scaled a system. What challenges did you face?"
     - Use their actual experience from resume in the answer

3. **Technical Deep-Dive:**
   - Based on skills mentioned in resume
   - Example: If resume mentions "Python and FastAPI":
     - Question: "How does async/await work in Python? When would you use FastAPI vs Flask?"

4. **Behavioral (STAR Method):**
   - Based on soft skills required in JD
   - Example: If JD mentions "team collaboration":
     - Question: "Tell me about a time you disagreed with a teammate. How did you handle it?"

5. **Company-Specific:**
   - Based on company info in JD
   - Example: If startup job mentions "fast-paced":
     - Question: "How do you handle ambiguity and changing priorities?"

**ANSWER FRAMEWORK (STAR method for behavioral):**
- Situation: Set the context
- Task: What needed to be done
- Action: What YOU specifically did
- Result: Quantified outcome

**PRIORITY RULES:**
- **High priority:** Questions about critical missing skills (80% chance they'll ask)
- **Medium priority:** Standard behavioral questions (60% chance)
- **Low priority:** Nice-to-have skills (30% chance)

**REQUIREMENTS:**
- Generate 6-8 questions total
- Include at least 2 gap-probing questions
- Include at least 2 behavioral questions
- Include at least 2 technical questions
- Make suggested answers reference their actual resume experience
- Be realistic - base on what interviewers actually ask

Return ONLY valid JSON, no other text."""

    @staticmethod
    def check_ats_compatibility(resume_text: str) -> str:
        """Enhanced ATS compatibility check"""
        return f"""Simulate how an Applicant Tracking System (ATS) would parse this resume. Be thorough and specific.

**RESUME TO ANALYZE:**
{resume_text}

Return analysis in this EXACT JSON format:

{{
  "ats_score": <integer 0-100>,
  "parsed_correctly": [
    "Elements successfully parsed (e.g., 'Contact information extracted', 'Work experience dates recognized')"
  ],
  "parsing_failures": [
    {{
      "issue": "Specific parsing failure",
      "severity": "critical|moderate|minor",
      "fix": "Exact action to fix it",
      "example": "Show the problematic text if applicable"
    }}
  ],
  "formatting_issues": [
    "Specific formatting problems (e.g., 'Two-column layout will confuse reading order', 'Special characters in section headers')"
  ],
  "recommendations": [
    "Prioritized list of fixes (most important first)"
  ],
  "keyword_optimization": {{
    "total_keywords": <count>,
    "keyword_density": "low|medium|high",
    "suggestions": ["Keywords that could be added naturally"]
  }}
}}

**ATS PARSING SIMULATION RULES:**

1. **CRITICAL FAILURES (Score impact: -30 points each):**
   - Contact info in header/footer (ATS skips these sections)
   - Two-column layout (confuses reading order)
   - Tables for experience/education (often unparseable)
   - Images, graphics, or logos (invisible to ATS)
   - Non-standard section headers (e.g., "My Journey" instead of "Experience")

2. **MODERATE ISSUES (Score impact: -10 points each):**
   - Special characters (★, ♦, etc.) in text
   - Inconsistent date formats
   - Skills hidden in paragraphs instead of clear list
   - Complex formatting (borders, shading, text boxes)
   - Non-standard fonts (use Arial, Calibri, Times New Roman)

3. **MINOR ISSUES (Score impact: -5 points each):**
   - Acronyms without full term (e.g., "AWS" without "Amazon Web Services")
   - Missing keywords that appear in typical job descriptions
   - Overly creative job titles
   - Lack of location information

**SCORING SYSTEM:**
- Start at 100
- Subtract points for each issue
- Minimum score: 0

**SCORE INTERPRETATION:**
- 90-100: Excellent - ATS will parse perfectly
- 75-89: Good - Minor issues, mostly parseable
- 60-74: Fair - Needs improvements, some data may be lost
- 40-59: Poor - Major parsing issues, likely to be rejected
- 0-39: Critical - ATS will fail to parse most information

**COMMON ATS SYSTEMS TO CONSIDER:**
- Greenhouse (used by tech startups)
- Lever (modern, better parsing)
- Workday (used by enterprises, stricter parsing)
- Taleo (Oracle, older system, very strict)
- iCIMS (common in mid-market)

**CHECK FOR:**
1. **Contact Information:**
   - Is name, email, phone clearly visible?
   - Is it in the body (not header)?
   - Is formatting simple?

2. **Section Headers:**
   - Are standard headers used? (Experience, Education, Skills)
   - Are they clearly distinguishable?
   - Are they in plain text?

3. **Dates:**
   - Consistent format? (MM/YYYY or Month YYYY)
   - Clearly associated with jobs/education?

4. **Job Titles & Companies:**
   - Clearly separated?
   - Easy to identify?

5. **Skills:**
   - Listed clearly?
   - Both acronym and full term? (ML and Machine Learning)
   - Separated properly?

6. **Overall Structure:**
   - Simple, linear layout?
   - No complex formatting?
   - Standard fonts?

Return ONLY valid JSON, no other text."""

    # ===== WEEK 2: RAG-AWARE PROMPTS (not used yet) =====
    
    @staticmethod
    def analyze_with_rag_context(
        job_description: str,
        resume_text: str,
        retrieved_context: str
    ) -> str:
        """Week 2: Enhanced with similar successful matches"""
        return f"""You have access to similar successful job matches from our database.

**SIMILAR SUCCESSFUL APPLICATIONS:**
{retrieved_context}

**CURRENT JOB DESCRIPTION:**
{job_description}

**CURRENT RESUME:**
{resume_text}

Analyze the current match, learning from what worked in similar successful applications.
Pay attention to:
- Which skills/keywords appeared in successful matches
- How those candidates positioned their experience
- What differentiated successful vs unsuccessful applications"""

    # ===== WEEK 3: AGENT PROMPTS (not used yet) =====
    
    AGENT_ANALYZER_SYSTEM = """You are the Analyzer Agent - a specialized AI focused solely on requirement extraction and matching.

Your ONLY responsibilities:
1. Extract all requirements from job descriptions (required vs preferred)
2. Extract all qualifications from resumes
3. Calculate match scores with transparent methodology
4. Identify gaps and overlaps

You do NOT:
- Write resume improvements (that's the Writer Agent's job)
- Simulate ATS parsing (that's the ATS Agent's job)
- Predict interview questions (that's the Interview Agent's job)

Stay in your lane. Be precise. Show your work."""

    AGENT_WRITER_SYSTEM = """You are the Writer Agent - a specialized AI focused solely on resume optimization.

Your ONLY responsibilities:
1. Rewrite resume sections to include missing keywords
2. Improve bullet points for impact and clarity
3. Quantify accomplishments
4. Ensure ATS-friendly formatting

You receive analysis from the Analyzer Agent and focus purely on writing improvements.

Stay in your lane. Write clearly. Maintain truthfulness."""


# Singleton instance
_prompt_templates = PromptTemplates()


def get_prompts() -> PromptTemplates:
    """Get prompt templates instance"""
    return _prompt_templates