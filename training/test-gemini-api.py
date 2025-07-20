import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("❌ Please set your GEMINI_API_KEY in the .env file")
    print("   Get your API key from: https://makersuite.google.com/app/apikey")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Test embedding
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="This is a test sentence.",
            task_type="retrieval_document"
        )
        
        print("✅ Gemini API key is working!")
        print(f"   Embedding dimension: {len(result['embedding'])}")
        print("   Ready to run the training script!")
        
    except Exception as e:
        print(f"❌ Error with Gemini API: {e}")
        print("   Please check your API key and internet connection")
