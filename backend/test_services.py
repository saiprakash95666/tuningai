"""Test all services together"""

from app.services.analysis_service import get_analysis_service
from app.llm.client import get_llm_client
from dotenv import load_dotenv
import json

load_dotenv()

print("=" * 60)
print("Testing TuningAI Services")
print("=" * 60)
print()

# Test data
job_desc = """
Senior Python Developer

We're looking for an experienced Python developer with:
- 5+ years Python experience
- FastAPI or Django framework experience
- AWS deployment experience
- Strong SQL skills
- Experience with Docker

Responsibilities:
- Build scalable REST APIs
- Deploy to AWS
- Work with data team on SQL queries
"""

resume = """
JOHN DOE
Senior Software Engineer

EXPERIENCE:
Software Engineer at TechCorp (2019-2024)
- Built REST APIs using Python and Flask
- Deployed applications to AWS
- Worked with PostgreSQL databases
- Used Git for version control

SKILLS:
Python, Flask, AWS, PostgreSQL, Git
"""

print("📋 Job Description:")
print(job_desc[:200] + "...\n")

print("📄 Resume:")
print(resume[:200] + "...\n")

print("🧪 Testing Analysis Service...")
print()

analysis_service = get_analysis_service()

try:
    # Test analysis
    print("1️⃣  Analyzing match...")
    analysis = analysis_service.analyze_match(job_desc, resume)
    
    print(f"✅ Match Score: {analysis['match_score']}%")
    print(f"✅ Verdict: {analysis['verdict']}")
    print(f"✅ Should Apply: {analysis['recommendation']['should_apply']}")
    print()
    
    print("💪 Strengths:")
    for strength in analysis['strengths'][:2]:
        print(f"   • {strength['point']}")
    print()
    
    print("⚠️  Weaknesses:")
    for weakness in analysis['weaknesses'][:2]:
        print(f"   • {weakness['point']}")
    print()
    
    # Test improvements
    print("2️⃣  Generating improvements...")
    improvements = analysis_service.generate_improvements(
        job_desc,
        resume,
        analysis
    )
    
    print(f"✅ Generated {len(improvements['improvements'])} improvements")
    print(f"   Example: {improvements['improvements'][0]['section']}")
    print()
    
    # Test interview questions
    print("3️⃣  Predicting interview questions...")
    questions = analysis_service.predict_interview_questions(
        job_desc,
        resume,
        analysis
    )
    
    print(f"✅ Generated {len(questions['questions'])} questions")
    print(f"   Example: {questions['questions'][0]['question'][:60]}...")
    print()
    
    # Test ATS check
    print("4️⃣  Checking ATS compatibility...")
    ats_check = analysis_service.check_ats_compatibility(resume)
    
    print(f"✅ ATS Score: {ats_check['ats_score']}%")
    print()
    
    print("=" * 60)
    print("🎉 ALL SERVICES WORKING PERFECTLY!")
    print("=" * 60)
    print()
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Debug info:")
    print(f"Type: {type(e)}")
    import traceback
    traceback.print_exc()