#!/usr/bin/env python3
"""
System Validation Script

Validates that all components of the AI Chatbot Training System are properly
configured and can connect to required services.

Run this script after installation to verify everything is working correctly.
"""

import os
import sys
import json
from dotenv import load_dotenv

def check_environment():
    """Check if environment variables are properly configured"""
    print("🔧 Checking Environment Configuration...")
    print("-" * 50)
    
    # Load environment
    load_dotenv()
    
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key',
        'QDRANT_URL': 'Qdrant database URL',
        'QDRANT_COLLECTION': 'Qdrant collection name'
    }
    
    optional_vars = {
        'RABBITMQ_URL': 'RabbitMQ connection URL',
        'QUEUE_NAME': 'Queue name for training tasks',
        'DOCS_ROOT_DIR': 'Default files directory'
    }
    
    all_good = True
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Missing ({description})")
            all_good = False
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"🔹 {var}: {display_value}")
        else:
            print(f"⚪ {var}: Not set ({description})")
    
    return all_good

def check_dependencies():
    """Check if all required Python packages are installed"""
    print("\n📦 Checking Python Dependencies...")
    print("-" * 50)
    
    required_packages = [
        'google.generativeai',
        'qdrant_client', 
        'langchain',
        'langchain_community',
        'pika',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_gemini_api():
    """Test connection to Google Gemini API"""
    print("\n🧠 Testing Gemini API Connection...")
    print("-" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with a simple embedding
        model = genai.GenerativeModel('models/text-embedding-004')
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="test connection"
        )
        
        if result and 'embedding' in result:
            print(f"✅ API connection successful")
            print(f"📊 Embedding dimension: {len(result['embedding'])}")
            return True
        else:
            print("❌ Invalid response from API")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def check_qdrant():
    """Test connection to Qdrant database"""
    print("\n🗄️ Testing Qdrant Connection...")
    print("-" * 50)
    
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = QdrantClient(url=qdrant_url)
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful")
        print(f"📊 Available collections: {len(collections.collections)}")
        
        # Check if our collection exists
        collection_name = os.getenv("QDRANT_COLLECTION", "chatbot-docs")
        if client.collection_exists(collection_name):
            info = client.get_collection(collection_name)
            print(f"📦 Collection '{collection_name}' exists with {info.points_count} points")
        else:
            print(f"📦 Collection '{collection_name}' will be created on first use")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("💡 Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        return False

def check_rabbitmq():
    """Test connection to RabbitMQ (optional)"""
    print("\n🐰 Testing RabbitMQ Connection...")
    print("-" * 50)
    
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    if not rabbitmq_url:
        print("⚪ RABBITMQ_URL not configured (optional for queue-based training)")
        return True
    
    try:
        import pika
        import ssl
        import urllib.parse
        
        # Parse URL to check if SSL is needed
        parsed_url = urllib.parse.urlparse(rabbitmq_url)
        
        if parsed_url.scheme == 'amqps':
            # SSL connection
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            params = pika.URLParameters(rabbitmq_url)
            params.ssl_options = pika.SSLOptions(ssl_context)
            connection = pika.BlockingConnection(params)
        else:
            # Regular connection
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        
        channel = connection.channel()
        queue_name = os.getenv("QUEUE_NAME", "test")
        
        # Check if queue exists or can be created
        try:
            method = channel.queue_declare(queue=queue_name, passive=True)
            print(f"✅ Queue '{queue_name}' exists with {method.method.message_count} messages")
        except:
            print(f"📦 Queue '{queue_name}' will be created on first use")
        
        connection.close()
        print(f"✅ RabbitMQ connection successful")
        return True
        
    except Exception as e:
        print(f"❌ RabbitMQ connection failed: {e}")
        print("💡 Check your RABBITMQ_URL or disable queue-based training")
        return False

def main():
    """Main validation function"""
    print("🚀 AI Chatbot Training System - Validation")
    print("=" * 60)
    
    # Track overall status
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies), 
        ("Gemini API", check_gemini_api),
        ("Qdrant", check_qdrant),
        ("RabbitMQ", check_rabbitmq)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results[name] = False
    
    # Summary
    print("\n📋 Validation Summary")
    print("=" * 60)
    
    required_checks = ["Environment", "Dependencies", "Gemini API", "Qdrant"]
    optional_checks = ["RabbitMQ"]
    
    required_passed = all(results.get(check, False) for check in required_checks)
    optional_passed = results.get("RabbitMQ", True)  # True if not configured
    
    for check in required_checks:
        status = "✅ PASS" if results.get(check, False) else "❌ FAIL"
        print(f"{check:15} {status}")
    
    for check in optional_checks:
        status = "✅ PASS" if results.get(check, False) else "⚪ SKIP"
        print(f"{check:15} {status}")
    
    if required_passed:
        print("\n🎉 All required components are working!")
        print("🚀 You can now run: python3 training-job-gemini.py")
        
        if not optional_passed:
            print("💡 For queue-based training, configure RabbitMQ settings")
    else:
        print("\n⚠️ Some required components need attention")
        print("🔧 Please fix the issues above before running the training system")
        sys.exit(1)

if __name__ == "__main__":
    main()
