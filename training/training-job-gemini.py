import os
import json
import pika
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chatbot-docs")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "embedding_tasks")
ROOT_DIR = os.getenv("DOCS_ROOT_DIR", "../chatbot-docs/")

# Configure Gemini
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env")
genai.configure(api_key=GEMINI_API_KEY)

# Init Qdrant
client = QdrantClient(url=QDRANT_URL)

def get_embedding(text, model="models/text-embedding-004"):
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def process_file(file_path):
    docs_count = 0
    abs_path = os.path.join(ROOT_DIR, file_path)
    print(f"📄 Processing file: {abs_path}")

    loader = TextLoader(abs_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = loader.load_and_split(splitter)

    points = []
    for i, doc in enumerate(documents):
        embedding = get_embedding(doc.page_content)
        if embedding:
            points.append(PointStruct(
                id=docs_count + i,
                vector=embedding,
                payload={
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "file_path": file_path
                }
            ))

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Uploaded {len(points)} chunks from {file_path}")
    else:
        print(f"⚠️ No embeddings created for {file_path}")

# RabbitMQ callback
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        file_path = data.get("file_path")
        if not file_path:
            print("❌ Invalid message format")
            return

        if not client.collection_exists(COLLECTION_NAME):
            print(f"⚠️ Collection '{COLLECTION_NAME}' not found. Creating it...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )

        process_file(file_path)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def start_worker():
    print(f"🔁 Listening for tasks on queue '{QUEUE_NAME}'...")
    
    try:
        # Handle SSL connection for CloudAMQP
        import ssl
        import urllib.parse
        
        # Parse the URL to check if it's SSL
        parsed_url = urllib.parse.urlparse(RABBITMQ_URL)
        
        if parsed_url.scheme == 'amqps':
            # Create SSL context for CloudAMQP
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connection parameters with SSL
            params = pika.URLParameters(RABBITMQ_URL)
            params.ssl_options = pika.SSLOptions(ssl_context)
            connection = pika.BlockingConnection(params)
        else:
            # Regular connection for local RabbitMQ
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
        
        print(f"✅ Connected to RabbitMQ successfully!")
        print(f"📥 Waiting for messages on queue '{QUEUE_NAME}'. To exit press CTRL+C")
        channel.start_consuming()
        
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ: {e}")
        print(f"🔗 URL: {RABBITMQ_URL}")
        raise

if __name__ == "__main__":
    start_worker()
