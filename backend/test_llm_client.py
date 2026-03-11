"""Test LLM client"""

from app.llm.client import get_llm_client
from dotenv import load_dotenv

load_dotenv()

# Test basic generation
llm = get_llm_client()

print("🧪 Testing basic generation...")
response = llm.generate(
    prompt="Explain what TuningAI does in one sentence.",
    system_prompt="You are a helpful assistant in job search."
)
print(f"✅ Response: {response}\n")

# Test structured output
print("🧪 Testing structured JSON output...")
response = llm.generate_structured(
    prompt="""Analyze this resume vs job:
    
Job: "Looking for Python developer with 3+ years experience"
Resume: "Senior Python Developer with 5 years experience"

Return a JSON with: {{"match_score": 0-100, "verdict": "APPLY or DON'T APPLY"}}""",
    system_prompt="You are a resume analyzer."
)
print(f"✅ Structured response: {response}\n")

print("🎉 LLM Client is working perfectly!")