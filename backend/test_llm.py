"""Test LLM connection to make sure API keys work"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def test_anthropic():
    """Test Anthropic Claude API"""
    print("🧪 Testing Anthropic Claude API...")
    
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'TuningAI is ready to help you get hired!' in a creative way."
                }
            ]
        )
        
        print("✅ SUCCESS! Anthropic API is working!")
        print(f"\n💬 Claude says:\n{response.content[0].text}\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 Check your ANTHROPIC_API_KEY in .env file")
        return False


if __name__ == "__main__":
    print("="*60)
    print("TuningAI - API Connection Test")
    print("="*60)
    print()
    
    success = test_anthropic()
    
    print()
    print("="*60)
    if success:
        print("🎉 All systems ready! You can start building!")
    else:
        print("⚠️  Fix API keys before proceeding")
    print("="*60)