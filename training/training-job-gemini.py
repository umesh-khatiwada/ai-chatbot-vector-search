import google.generativeai as genai
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("❌ Please set your GEMINI_API_KEY in the .env file")
    print("   Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text, model="models/text-embedding-004"):
    """Get embedding from Gemini API"""
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

# File paths to process
file_paths = (
    "content/faq.md",
)
docs_count = 0
files_count = 0
root_dir = "../chatbot-docs/"  # Updated path since we're in training/ directory

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
client = QdrantClient(url=qdrant_url)
collection_name = os.getenv("COLLECTION_NAME", "chatbot-docs")

# Check if collection exists and delete it for fresh start
try:
    client.delete_collection(collection_name)
    print(f"Deleted existing collection: {collection_name}")
except:
    print(f"Collection {collection_name} doesn't exist yet")

# Create collection with embedding dimension (768 for Gemini text-embedding-004)
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)
print(f"Created collection: {collection_name}")

# Process each file
for file_path in file_paths:
    files_count += 1
    print(f"Loading file {files_count}: {file_path}")
    
    # Load document
    loader = TextLoader(root_dir + file_path)
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = loader.load_and_split(text_splitter)
    print(f"Text split into {len(documents)} chunks")
    
    # Create embeddings and points for Qdrant
    points = []
    for i, doc in enumerate(documents):
        print(f"Creating embedding for chunk {i+1}/{len(documents)}")
        
        # Get embedding from Gemini
        embedding = get_embedding(doc.page_content)
        
        if embedding is not None:
            points.append(PointStruct(
                id=docs_count + i,
                vector=embedding,
                payload={
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "file_path": file_path
                }
            ))
        else:
            print(f"Failed to get embedding for chunk {i+1}")
    
    # Upload points to Qdrant
    if points:
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print(f"Uploaded {len(points)} document chunks to Qdrant")
        docs_count += len(points)
    else:
        print("No valid embeddings created")

print(f"\n✅ Completed embedding process!")
print(f"Total files processed: {files_count}")
print(f"Total document chunks embedded: {docs_count}")
print(f"Collection '{collection_name}' is ready for use")
