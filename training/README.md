# 🔄 Training Pipeline

Document processing and embedding pipeline that prepares your knowledge base for the AI chatbot using Google Gemini API and Qdrant vector database.

## 🎯 Purpose

This training pipeline:
- 📄 **Processes** your documents (PDF, Markdown, Text)
- ✂️ **Splits** them into semantic chunks
- 🧠 **Creates** embeddings using Gemini API
- 💾 **Stores** vectors in Qdrant for fast retrieval

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Qdrant database running locally or in cloud

### 2. Install Dependencies

```bash
# Make sure you're in the training directory
cd training

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Additional packages for Gemini API
pip install google-generativeai python-dotenv
```

### 3. Set Up Environment

Create a `.env` file in this directory:

```bash
# Gemini API Key (required)
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=chatbot-docs

# Optional: For Qdrant Cloud
# APIKEY=your_qdrant_cloud_api_key
```

### 4. Start Qdrant Database

```bash
# Using Docker (recommended)
docker run -d -p 6333:6333 --name qdrant-local qdrant/qdrant:latest

# Verify it's running
curl http://localhost:6333/health
```

### 5. Prepare Your Documents

```bash
# Create document directory structure
mkdir -p ../chatbot-docs/content

# Add your documents to the content directory
# Supported formats: .md, .txt, .pdf
```

Example structure:
```
../chatbot-docs/
└── content/
    ├── faq.md
    ├── user-guide.md
    ├── api-docs.pdf
    └── troubleshooting.txt
```

### 6. Configure Document Paths

Edit the file paths in your training script:

```python
# In training-job-gemini.py
file_paths = (
    "content/faq.md",
    "content/user-guide.md", 
    "content/api-docs.pdf",
    # Add more files as needed
)
```

### 7. Run Training

```bash
# Test your API key first
python3 test-gemini-api.py

# Run the training pipeline
python3 training-job-gemini.py
```

## 📋 Available Scripts

| Script | Description | Use Case |
|--------|-------------|----------|
| `training-job-gemini.py` | Main training with Gemini API | **Recommended** |
| `training-job-chatbot.py` | Original Vertex AI version | Legacy/GCP billing |
| `test-gemini-api.py` | API connectivity test | Troubleshooting |
| `test-setup.py` | Qdrant setup with dummy data | Testing |

## ⚙️ Configuration

### Document Processing Settings

```python
# Text splitting configuration
chunk_size = 1000        # Characters per chunk
chunk_overlap = 0        # Overlap between chunks

# Embedding model
model = "models/text-embedding-004"  # Gemini embedding model

# Qdrant configuration
collection_name = "chatbot-docs"
vector_size = 768        # Embedding dimension
distance = Distance.COSINE
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `QDRANT_URL` | Qdrant database URL | `http://localhost:6333` |
| `COLLECTION_NAME` | Vector collection name | `chatbot-docs` |
| `APIKEY` | Qdrant Cloud API key | Optional |

## 📊 Training Process

### Step-by-Step Workflow

1. **Document Loading** 📄
   ```
   Load files → Validate format → Extract text
   ```

2. **Text Splitting** ✂️
   ```
   Raw text → Semantic chunks → Overlap handling
   ```

3. **Embedding Creation** 🧠
   ```
   Text chunks → Gemini API → Vector embeddings
   ```

4. **Vector Storage** 💾
   ```
   Embeddings → Qdrant → Indexed for search
   ```

### Expected Output

```bash
Loading file 1: content/faq.md
Text split into 5 chunks
Creating embedding for chunk 1/5
Creating embedding for chunk 2/5
...
Uploaded 5 document chunks to Qdrant

✅ Completed embedding process!
Total files processed: 1
Total document chunks embedded: 5
Collection 'chatbot-docs' is ready for use
```

## 🔧 Advanced Configuration

### Custom Document Processing

```python
# Custom text splitter
from langchain.text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1500,
    chunk_overlap=200,
    length_function=len,
)
```

### Batch Processing

For large document sets:

```python
# Process documents in batches
batch_size = 10
for i in range(0, len(file_paths), batch_size):
    batch = file_paths[i:i+batch_size]
    process_batch(batch)
```

### Custom Metadata

Add metadata to improve search:

```python
points.append(PointStruct(
    id=doc_id,
    vector=embedding,
    payload={
        "text": doc.page_content,
        "source": file_path,
        "chunk_id": chunk_id,
        "document_type": "faq",
        "created_at": datetime.now().isoformat(),
    }
))
```

## 🐛 Troubleshooting

### Common Issues

#### 🔴 API Key Error
```bash
# Test your API key
python3 test-gemini-api.py

# Check environment file
cat .env | grep GEMINI_API_KEY
```

#### 🔴 Qdrant Connection Failed
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Test connection
curl http://localhost:6333/collections
```

#### 📄 File Not Found
```bash
# Check file paths
ls -la ../chatbot-docs/content/

# Verify file permissions
chmod 644 ../chatbot-docs/content/*.md
```

#### 🧠 Embedding Errors
- **Rate limiting**: Add delays between API calls
- **Content too long**: Reduce chunk size
- **Invalid characters**: Clean text before embedding

### Debug Mode

```bash
# Run with debug output
python3 -v training-job-gemini.py

# Check specific errors
python3 training-job-gemini.py 2>&1 | tee training.log
```

## 📊 Performance Optimization

### Speed Improvements

```python
# Parallel processing (be careful with API limits)
import asyncio
import aiohttp

async def embed_batch(texts):
    # Implement async embedding
    pass

# Caching embeddings
import pickle

def cache_embeddings(embeddings, filename):
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)
```

### Memory Management

```python
# Process large files in chunks
def process_large_file(file_path, chunk_size=1000):
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
```

## 🔍 Quality Assurance

### Verify Training Results

```bash
# Check collection info
curl http://localhost:6333/collections/chatbot-docs

# Test search functionality
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://localhost:6333')
results = client.search(
    collection_name='chatbot-docs',
    query_vector=[0.1] * 768,  # Dummy vector
    limit=3
)
print(f'Found {len(results)} results')
"
```

### Document Coverage Analysis

```python
# Analyze document distribution
def analyze_collection():
    results = client.scroll(collection_name, limit=100)
    sources = {}
    for point in results[0]:
        source = point.payload.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    return sources
```

## 🚀 Production Deployment

### Automation

```bash
# Create a training script
#!/bin/bash
set -e

echo "Starting training pipeline..."
cd training
source venv/bin/activate
python3 training-job-gemini.py
echo "Training completed successfully!"
```

### Monitoring

```python
# Add logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
```

### Scheduled Updates

```bash
# Add to crontab for daily updates
0 2 * * * /path/to/training/update_embeddings.sh
```

## 📈 Scaling Considerations

### Large Document Sets

- **Batch processing**: Process files in smaller groups
- **Incremental updates**: Only re-process changed documents
- **Distributed processing**: Use multiple workers
- **Cloud storage**: Store documents in cloud for better access

### API Rate Limits

- **Gemini Free Tier**: 60 requests per minute
- **Add delays**: Use `time.sleep()` between requests
- **Implement retries**: Handle temporary failures
- **Consider paid tier**: For production workloads

## 🔗 Integration

### CI/CD Pipeline

```yaml
# GitHub Actions example
name: Update Knowledge Base
on:
  push:
    paths: ['docs/**']
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run training
        run: |
          cd training
          pip install -r requirements.txt
          python3 training-job-gemini.py
```

### API Integration

```python
# REST API for training triggers
from flask import Flask, request

app = Flask(__name__)

@app.route('/retrain', methods=['POST'])
def trigger_retrain():
    # Trigger training pipeline
    result = subprocess.run(['python3', 'training-job-gemini.py'])
    return {'status': 'success' if result.returncode == 0 else 'error'}
```

## 📞 Support

- **Training Issues**: Check logs and error messages
- **API Problems**: [Google AI Studio Help](https://aistudio.google.com/app/help)
- **Qdrant Issues**: [Qdrant Documentation](https://qdrant.tech/documentation/)
- **Performance**: Monitor API usage and rate limits

## 🔗 Related Files

- `../chatbot/` - Chatbot application that uses trained data
- `../README.md` - Complete project documentation
- `requirements.txt` - Python dependencies
- `.env.example` - Environment configuration template
