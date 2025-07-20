from langchain_openai import OpenAIEmbeddings
# from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
import os

file_paths = (
    "content/faq.md",
)
docs_count = 0
files_count = 0
root_dir = "./chatbot-docs/"
for file_path in file_paths:
    files_count += 1
    print(f"Loading file {files_count}")
    # loader = PyPDFLoader(file_path)
    loader = TextLoader(root_dir + file_path)

    # [START gke_databases_qdrant_docker_embed_docs_split]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = loader.load_and_split(text_splitter)
    # [END gke_databases_qdrant_docker_embed_docs_split]
    print("Text splitted")

    # [START gke_databases_qdrant_docker_embed_docs_embed]
    # For testing without billing, you can use a simple embedding or comment this out
    # embeddings = VertexAIEmbeddings("text-embedding-005")
    # Alternative: use OpenAI embeddings (requires OPENAI_API_KEY environment variable)
    embeddings = OpenAIEmbeddings()
    # [END gke_databases_qdrant_docker_embed_docs_embed]
    print("Embeddings created")

    # [START gke_databases_qdrant_docker_embed_docs_storage]
    qdrant = Qdrant.from_documents(
        documents,
        embeddings,
        # collection_name=os.getenv("COLLECTION_NAME"),
        # url=os.getenv("QDRANT_URL"),
        # api_key=os.getenv("APIKEY"),
        collection_name="chatbot-docs",
        url="http://localhost:6333",
        shard_number=6,
        replication_factor=2,
    )
    # [END gke_databases_qdrant_docker_embed_docs_storage]
    print(f"Embedded with {len(documents)} docs")
    docs_count += len(documents)
print(f"Completed embedding with {files_count} files and {docs_count} docs")
