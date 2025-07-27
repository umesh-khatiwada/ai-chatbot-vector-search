import os
import json
import pika
import ssl
import urllib.parse
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("APIKEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "chatbot-docs")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "embedding_tasks")
ROOT_DIR = os.getenv("DOCS_ROOT_DIR", "./chatbot-docs/content")

# Configure Gemini
if not GEMINI_API_KEY:
    raise ValueError(" GEMINI_API_KEY is missing in .env")
genai.configure(api_key=GEMINI_API_KEY)

# Init Qdrant with better error handling
def init_qdrant_client():
    """Initialize Qdrant client with proper error handling"""
    try:
        if QDRANT_API_KEY:
            print(f" Connecting to Qdrant with API key authentication")
            print(f"🔗 URL: {QDRANT_URL}")
            try:
                client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
                client.get_collections()
                print(f" Successfully connected to Qdrant!")
                return client
            except Exception as e1:
                print(f" First attempt failed: {e1}")
                if not QDRANT_URL.endswith(':6333') and not QDRANT_URL.endswith(':443'):
                    url_with_port = QDRANT_URL + ':443' if QDRANT_URL.startswith('https') else QDRANT_URL + ':6333'
                    print(f" Trying with explicit port: {url_with_port}")
                    try:
                        client = QdrantClient(url=url_with_port, api_key=QDRANT_API_KEY)
                        client.get_collections()
                        print(f" Successfully connected with port!")
                        return client
                    except Exception as e2:
                        print(f" Port attempt failed: {e2}")
                print(f" Trying with timeout settings...")
                try:
                    client = QdrantClient(
                        url=QDRANT_URL, 
                        api_key=QDRANT_API_KEY,
                        timeout=30,
                        prefer_grpc=False
                    )
                    client.get_collections()
                    print(f" Successfully connected with timeout settings!")
                    return client
                except Exception as e3:
                    print(f" All connection attempts failed: {e3}")
                    raise e3
        else:
            print(f" Connecting to Qdrant without authentication")
            client = QdrantClient(url=QDRANT_URL)
            client.get_collections()
            return client
            
    except Exception as e:
        print(f" Failed to connect to Qdrant: {e}")
        print(f"URL: {QDRANT_URL}")
        print(f"API Key: {'Set' if QDRANT_API_KEY else 'Not Set'}")
        return None

# Initialize Qdrant client
client = init_qdrant_client()

def get_embedding(text, model="models/text-embedding-004"):
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f" Error getting embedding: {e}")
        return None

def process_file(file_path, docs_count=0):
    """Process a single file and return the number of documents processed"""
    abs_path = os.path.join(ROOT_DIR, file_path)
    print(f" Processing file: {abs_path}")
    if not os.path.exists(abs_path):
        print(f" File not found: {abs_path}")
        return 0

    try:
        loader = TextLoader(abs_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = loader.load_and_split(splitter)
        print(f" Split into {len(documents)} chunks")
        points = []
        for i, doc in enumerate(documents):
            print(f" Creating embedding for chunk {i+1}/{len(documents)}")
            embedding = get_embedding(doc.page_content)
            if embedding:
                points.append(PointStruct(
                    id=docs_count + i,
                    vector=embedding,
                    payload={
                        "text": doc.page_content,
                        "metadata": doc.metadata,
                        "file_path": file_path,
                        "chunk_index": i,
                        "total_chunks": len(documents)
                    }
                ))

        if points:
            if not client:
                print(f" Qdrant client not available. Cannot upload chunks.")
                return 0
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f" Uploaded {len(points)} chunks from {file_path}")
            return len(points)
        else:
            print(f" No embeddings created for {file_path}")
            return 0
            
    except Exception as e:
        print(f" Error processing file {file_path}: {e}")
        return 0

def process_content_directly(content, document_id, source, docs_count=0):
    print(f" Processing content for document: {document_id}")
    print(f" Starting point ID: {docs_count}")
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = splitter.split_text(content)
        print(f" Split into {len(documents)} chunks")
        
        if len(documents) == 0:
            print(f" No chunks created from content")
            return 0

        points = []
        successful_embeddings = 0
        failed_embeddings = 0
        
        for i, doc_content in enumerate(documents):
            print(f" Creating embedding for chunk {i+1}/{len(documents)} (ID: {docs_count + i})")
            embedding = get_embedding(doc_content)
            if embedding:
                successful_embeddings += 1
                points.append(PointStruct(
                    id=docs_count + i,
                    vector=embedding,
                    payload={
                        "text": doc_content,
                        "document_id": document_id,
                        "source": source,
                        "chunk_index": i,
                        "total_chunks": len(documents),
                        "type": "queue_content",
                        "chunk_length": len(doc_content)
                    }
                ))
            else:
                failed_embeddings += 1
                print(f" Failed to create embedding for chunk {i+1}")

        print(f" Embedding results: {successful_embeddings} successful, {failed_embeddings} failed")

        if points:
            if not client:
                print(f" Qdrant client not available. Cannot upload chunks.")
                return 0
            print(f" Uploading {len(points)} points to Qdrant...")
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f" Uploaded {len(points)} chunks from content: {document_id}")
            return len(points)
        else:
            print(f" No embeddings created for content: {document_id}")
            return 0
            
    except Exception as e:
        print(f" Error processing content {document_id}: {e}")
        import traceback
        print(f" Full error traceback:")
        traceback.print_exc()
        return 0

def train_default_files():
    default_files = [
        "faq.md",
    ]
    if not os.path.exists(ROOT_DIR):
        print(f" Root directory not found: {ROOT_DIR}")
        print("📁 Creating directory...")
        os.makedirs(ROOT_DIR, exist_ok=True)
        sample_faq_path = os.path.join(ROOT_DIR, "faq.md")
        if not os.path.exists(sample_faq_path):
            sample_content = """# Frequently Asked Questions

## What is this chatbot?
This is an AI-powered chatbot that can answer questions based on trained documents.

## How does it work?
The chatbot uses vector embeddings to find relevant information and generate responses.

## Can I add more content?
Yes! You can add content through the queue system or by placing files in the content directory.
"""
            with open(sample_faq_path, 'w') as f:
                f.write(sample_content)
            print(f" Created sample FAQ file: {sample_faq_path}")
    actual_files = []
    for file_name in os.listdir(ROOT_DIR):
        if file_name.endswith(('.md', '.txt')):
            actual_files.append(file_name)
    
    if not actual_files:
        print(f" No .md or .txt files found in {ROOT_DIR}")
        return 0
    
    print(f" Found {len(actual_files)} files to process:")
    for file_name in actual_files:
        print(f"  - {file_name}")
    try:
        if not client:
            print(f" Qdrant client not available. Skipping training.")
            return 0
            
        if not client.collection_exists(COLLECTION_NAME):
            print(f" Collection '{COLLECTION_NAME}' not found. Creating it...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
            print(f" Created collection: {COLLECTION_NAME}")
        else:
            print(f" Using existing collection: {COLLECTION_NAME}")
    except Exception as e:
        return 0
    
    # Process each file
    total_docs = 0
    files_processed = 0
    
    for file_name in actual_files:
        docs_added = process_file(file_name, total_docs)
        if docs_added > 0:
            total_docs += docs_added
            files_processed += 1
        print("-" * 30)
    
    print(f"\n Default training completed!")
    print(f" Files processed: {files_processed}/{len(actual_files)}")
    print(f" Total document chunks: {total_docs}")
    print(f" Collection: {COLLECTION_NAME}")
    
    return total_docs

# RabbitMQ callback
def callback(ch, method, properties, body):
    try:
        print(f"\n Received message from queue...")
        print(f"📋 Message size: {len(body)} bytes")
        try:
            raw_content = body.decode('utf-8')
            print(f" Raw content: '{raw_content}'")
        except UnicodeDecodeError:
            print(f" Raw content (bytes): {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        try:
            data = json.loads(raw_content)
            print(f"Successfully parsed as direct JSON")
        except json.JSONDecodeError:
            print(f"Not valid JSON, treating as plain text content")
            if len(raw_content.strip()) > 0:
                data = {
                    "content": raw_content,
                    "document_id": f"plain_text_{hash(raw_content) % 100000}",
                    "source": "queue_plain_text",
                    "timestamp": "unknown"
                }
                print(f"Converted plain text to content format")
            else:
                print(f" Empty or invalid message content")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        
        print(f" Message type: {'content-based' if 'content' in data else 'file-based'}")
        if "content" in data:
            content = data.get("content")
            document_id = data.get("document_id", "unknown")
            source = data.get("source", "queue")
            timestamp = data.get("timestamp", "unknown")
            
            if not content or len(content.strip()) == 0:
                print("Invalid message format - missing or empty content")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            print(f"Processing content message:")
            print(f" Document ID: {document_id}")
            print(f"Source: {source}")
            print(f"Timestamp: {timestamp}")
            print(f"Content length: {len(content)} characters")
            if not client:
                print(" Qdrant client not available. Cannot process content.")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            try:
                if not client.collection_exists(COLLECTION_NAME):
                    print(f" Collection '{COLLECTION_NAME}' not found. Creating it...")
                    client.create_collection(
                        collection_name=COLLECTION_NAME,
                        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                    )
                    print(f" Created collection: {COLLECTION_NAME}")
            except Exception as coll_error:
                print(f" Error with collection: {coll_error}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return

            try:
                collection_info = client.get_collection(COLLECTION_NAME)
                current_count = collection_info.points_count
                print(f" Current collection has {current_count} points")
            except Exception as count_error:
                print(f" Could not get collection count: {count_error}")
                current_count = 0
            
            docs_added = process_content_directly(content, document_id, source, current_count)
            
            if docs_added > 0:
                print(f" Successfully processed queue content: {document_id}")
                print(f" Added {docs_added} new chunks to collection")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f" No documents added for: {document_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag) 
                
        else:
            file_path = data.get("file_path")
            if not file_path:
                print(" Invalid message format - missing file_path or content")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            print(f"\n Received queue message for file: {file_path}")
            if not client.collection_exists(COLLECTION_NAME):
                print(f" Collection '{COLLECTION_NAME}' not found. Creating it...")
                client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )
            collection_info = client.get_collection(COLLECTION_NAME)
            current_count = collection_info.points_count
            
            docs_added = process_file(file_path, current_count)
            
            if docs_added > 0:
                print(f" Successfully processed queue message: {file_path}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f" No documents added for: {file_path}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
    except Exception as e:
        print(f" Error processing queue message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    """Start the training worker - first train default files, then listen for queue messages"""
    
    # Step 1: Train default files
    print("🎯 PHASE 1: Training Default Files")
    print("=" * 60)
    
    try:
        default_docs_count = train_default_files()
        print(f"\n Phase 1 completed! Trained {default_docs_count} document chunks")
    except Exception as e:
        print(f" Error in default training: {e}")
        print(" Continuing to queue listener despite error...")
    
    # Step 2: Start queue listener
    print("PHASE 2: Starting Queue Listener")
    print("=" * 60)
    print(f"Listening for tasks on queue '{QUEUE_NAME}'...")
    
    try:
        import ssl
        import urllib.parse
        import time
        parsed_url = urllib.parse.urlparse(RABBITMQ_URL)
        
        max_retries = 3
        retry_count = 0
        connection = None
        
        while retry_count < max_retries and connection is None:
            try:
                if parsed_url.scheme == 'amqps':
                    print("Using SSL connection for CloudAMQP")
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    params = pika.URLParameters(RABBITMQ_URL)
                    params.ssl_options = pika.SSLOptions(ssl_context)
                    params.connection_attempts = 3
                    params.retry_delay = 2
                    params.socket_timeout = 30
                    params.heartbeat = 600
                    params.blocked_connection_timeout = 300
                    
                    print(f" Attempting to connect (try {retry_count + 1}/{max_retries})...")
                    connection = pika.BlockingConnection(params)
                else:
                    print("🔓 Using regular connection for local RabbitMQ")
                    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
                
                print(" Successfully connected to RabbitMQ!")
                break
                
            except Exception as conn_error:
                retry_count += 1
                print(f" Connection attempt {retry_count} failed: {conn_error}")
                
                if retry_count < max_retries:
                    wait_time = retry_count * 5
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"Troubleshooting tips:")
                    print(f"   - Check if CloudAMQP instance is running")
                    print(f"   - Verify your CloudAMQP URL and credentials")
                    print(f"   - Check firewall/network connectivity")
                    print(f"   - Try using a different CloudAMQP region")
                    raise conn_error
        
        if connection is None:
            raise Exception("Failed to establish connection after all retries")
        
        channel = connection.channel()
        try:
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print(f" Queue '{QUEUE_NAME}' declared successfully")
        except Exception as queue_error:
            print(f" Queue declaration failed: {queue_error}")
            print(f" Trying passive mode (using existing queue)...")
            try:
                channel.close()
            except:
                pass
            
            try:
                channel = connection.channel()
                method = channel.queue_declare(queue=QUEUE_NAME, passive=True)
                print(f" Using existing queue '{QUEUE_NAME}' with {method.method.message_count} messages")
            except Exception as passive_error:
                print(f" Passive declaration also failed: {passive_error}")
                print(f" Try using the manage_queue.py script to reset the queue")
                connection.close()
                raise passive_error
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
        
        print(f" Connected to RabbitMQ successfully!")
        print(f" Waiting for messages on queue '{QUEUE_NAME}'")
        print(f" To exit press CTRL+C")
        print("-" * 60)
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n Received interrupt signal. Shutting down gracefully...")
        try:
            channel.stop_consuming()
            connection.close()
        except:
            pass
    except Exception as e:
        print(f" Failed to connect to RabbitMQ: {e}")
        print(f" URL: {RABBITMQ_URL}")
        raise

if __name__ == "__main__":
    print(" AI Chatbot Training System with Queue Support")
    print("=" * 60)
    print(f" Root Directory: {ROOT_DIR}")
    print(f" Qdrant URL: {QDRANT_URL}")
    print(f" Collection: {COLLECTION_NAME}")
    print(f" Queue: {QUEUE_NAME}")
    print("=" * 60)
    
    start_worker()
