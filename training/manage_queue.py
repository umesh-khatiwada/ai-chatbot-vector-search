#!/usr/bin/env python3
"""
CloudAMQP Queue Management Script
Helps manage queues in CloudAMQP with proper SSL handling
"""

import os
import json
import pika
import ssl
import urllib.parse
from dotenv import load_dotenv

# Load environment
load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "test")

def create_ssl_connection():
    """Create SSL connection to CloudAMQP"""
    try:
        # Parse the URL to check if it's SSL
        parsed_url = urllib.parse.urlparse(RABBITMQ_URL)
        
        if parsed_url.scheme == 'amqps':
            print("🔒 Using SSL connection to CloudAMQP")
            # Create SSL context for CloudAMQP
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connection parameters with SSL
            params = pika.URLParameters(RABBITMQ_URL)
            params.ssl_options = pika.SSLOptions(ssl_context)
            connection = pika.BlockingConnection(params)
        else:
            print("🔓 Using regular connection")
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        
        print("✅ Connected to RabbitMQ successfully!")
        return connection
        
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ: {e}")
        return None

def delete_queue():
    """Delete the problematic queue"""
    print(f"🗑️ Deleting queue: {QUEUE_NAME}")
    print("-" * 40)
    
    connection = create_ssl_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Check if queue exists first
        try:
            method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
            message_count = method.method.message_count
            print(f"📊 Queue exists with {message_count} messages")
        except Exception as e:
            print(f"⚠️ Queue doesn't exist or can't be accessed: {e}")
            connection.close()
            return False
        
        # Delete the queue
        channel.queue_delete(queue=QUEUE_NAME)
        print(f"✅ Successfully deleted queue: {QUEUE_NAME}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to delete queue: {e}")
        return False

def create_fresh_queue():
    """Create a fresh queue with correct parameters"""
    print(f"🆕 Creating fresh queue: {QUEUE_NAME}")
    print("-" * 40)
    
    connection = create_ssl_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Create queue with durable=True
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print(f"✅ Successfully created queue: {QUEUE_NAME}")
        
        # Verify the queue
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        message_count = method.method.message_count
        print(f"📊 Queue verified with {message_count} messages")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create queue: {e}")
        return False

def reset_queue():
    """Delete and recreate the queue"""
    print(f"🔄 Resetting queue: {QUEUE_NAME}")
    print("=" * 50)
    
    # Step 1: Delete existing queue
    if delete_queue():
        print("\n⏳ Waiting 2 seconds...")
        import time
        time.sleep(2)
        
        # Step 2: Create fresh queue
        if create_fresh_queue():
            print(f"\n🎉 Successfully reset queue: {QUEUE_NAME}")
            return True
    
    print(f"\n❌ Failed to reset queue: {QUEUE_NAME}")
    return False

def send_test_message():
    """Send a test message to the queue"""
    print(f"📤 Sending test message to: {QUEUE_NAME}")
    print("-" * 40)
    
    connection = create_ssl_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Use passive mode to check existing queue
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        print(f"📊 Queue has {method.method.message_count} messages before sending")
        
        # Create test message with content
        test_message = {
            "content": """# Sample Document for Training

## Introduction
This is a sample document that demonstrates how the queue-based training system works.

## Features
- Direct content processing without file I/O
- Automatic text chunking and embedding
- Vector storage in Qdrant database

## Benefits
- Faster processing as no file reading required
- More flexible content sources
- Real-time training capabilities

## How it Works
1. Content is sent via RabbitMQ queue
2. Training system receives the message
3. Content is split into chunks
4. Embeddings are created using Gemini API
5. Vectors are stored in Qdrant for search

This allows for dynamic content training without requiring file management!""",
            "document_id": "sample_content_001",
            "source": "test_script",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Send message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(test_message),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent
        )
        
        print(f"✅ Test message sent with content!")
        print(f"📄 Document ID: {test_message['document_id']}")
        print(f"📝 Content length: {len(test_message['content'])} characters")
        
        # Check queue again
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        print(f"📊 Queue now has {method.method.message_count} messages")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test message: {e}")
        return False

def send_custom_content():
    """Send a custom content message to the queue"""
    print(f"📝 Send Custom Content to: {QUEUE_NAME}")
    print("-" * 40)
    
    # Get custom content from user
    print("Enter your content (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    # Remove the last empty line
    if lines and lines[-1] == "":
        lines.pop()
    
    content = "\n".join(lines)
    
    if not content.strip():
        print("❌ No content provided!")
        return False
    
    document_id = input("Enter document ID (or press Enter for auto-generated): ").strip()
    if not document_id:
        import time
        document_id = f"custom_doc_{int(time.time())}"
    
    source = input("Enter source (or press Enter for 'manual'): ").strip()
    if not source:
        source = "manual"
    
    connection = create_ssl_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Use passive mode to check existing queue
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        print(f"📊 Queue has {method.method.message_count} messages before sending")
        
        # Create custom content message
        custom_message = {
            "content": content,
            "document_id": document_id,
            "source": source,
            "timestamp": f"{__import__('datetime').datetime.now().isoformat()}Z"
        }
        
        # Send message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(custom_message),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent
        )
        
        print(f"✅ Custom content sent!")
        print(f"📄 Document ID: {document_id}")
        print(f"📝 Content length: {len(content)} characters")
        print(f"🏷️ Source: {source}")
        
        # Check queue again
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        print(f"📊 Queue now has {method.method.message_count} messages")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send custom content: {e}")
        return False

def check_queue_status():
    """Check the current status of the queue"""
    print(f"📊 Checking queue status: {QUEUE_NAME}")
    print("-" * 40)
    
    connection = create_ssl_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Get queue info
        method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        message_count = method.method.message_count
        consumer_count = method.method.consumer_count
        
        print(f"Queue Name: {QUEUE_NAME}")
        print(f"Messages: {message_count}")
        print(f"Consumers: {consumer_count}")
        print(f"Status: {'Active' if consumer_count > 0 else 'No consumers'}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to check queue status: {e}")
        return False

def main():
    """Interactive menu"""
    print("🐰 CloudAMQP Queue Manager")
    print("=" * 50)
    print(f"Queue: {QUEUE_NAME}")
    print(f"URL: {RABBITMQ_URL[:50]}...")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Check queue status")
        print("2. Reset queue (delete + recreate)")
        print("3. Delete queue only")
        print("4. Create fresh queue")
        print("5. Send test message")
        print("6. Send custom content")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            check_queue_status()
        elif choice == "2":
            confirm = input(f"⚠️ This will delete all messages in '{QUEUE_NAME}'. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                reset_queue()
        elif choice == "3":
            confirm = input(f"⚠️ This will delete queue '{QUEUE_NAME}'. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_queue()
        elif choice == "4":
            create_fresh_queue()
        elif choice == "5":
            send_test_message()
        elif choice == "6":
            send_custom_content()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "reset":
            reset_queue()
        elif command == "delete":
            delete_queue()
        elif command == "create":
            create_fresh_queue()
        elif command == "status":
            check_queue_status()
        elif command == "send":
            send_test_message()
        elif command == "custom":
            send_custom_content()
        else:
            print("Usage: python3 manage_queue.py [reset|delete|create|status|send|custom]")
    else:
        main()
