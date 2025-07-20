from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import numpy as np

# Simple test script to set up Qdrant collection for testing
# This doesn't require Google Cloud billing

print("Setting up Qdrant collection for testing...")

# Initialize Qdrant client
client = QdrantClient(url="http://localhost:6333")
collection_name = "chatbot-docs"

# Check if collection exists and delete it for fresh start
try:
    client.delete_collection(collection_name)
    print(f"Deleted existing collection: {collection_name}")
except:
    print(f"Collection {collection_name} doesn't exist yet")

# Create collection with simple configuration
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

print(f"Created collection: {collection_name}")

# Load and split documents
file_paths = (
    "content/faq.md",
)
root_dir = "./chatbot-docs/"

for file_path in file_paths:
    print(f"Loading file: {file_path}")
    loader = TextLoader(root_dir + file_path)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = loader.load_and_split(text_splitter)
    print(f"Split into {len(documents)} chunks")
    
    # Create simple vectors for testing (normally you'd use real embeddings)
    # This creates random vectors just for testing the setup
    points = []
    for i, doc in enumerate(documents):
        # Create a simple vector (normally this would be from an embedding model)
        vector = np.random.random(384).tolist()
        
        points.append({
            "id": i,
            "vector": vector,
            "payload": {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
        })
    
    # Upload points to Qdrant
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"Uploaded {len(points)} documents to Qdrant")

print("\n✅ Test setup complete!")
print(f"Collection '{collection_name}' is ready with {len(points)} documents")
print("\nNote: This uses random vectors for testing.")
print("For production, you'll need to enable Google Cloud billing to use real embeddings.")
