# AI Chatbot Training System

Advanced training system with dual-mode processing: file-based and real-time queue-based content training using Google Gemini API and Qdrant vector database.

## 🚀 Features

- **Dual Training Modes**: File-based and queue-based content processing
- **Real-time Processing**: RabbitMQ integration for dynamic content updates  
- **Vector Embeddings**: Google Gemini API for high-quality text embeddings
- **Vector Storage**: Qdrant database for efficient similarity search
- **Cloud Queue Support**: CloudAMQP with SSL/TLS security
- **Flexible Content**: Direct content or file-based training
- **Error Recovery**: Comprehensive error handling and retry mechanisms

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Qdrant vector database
- RabbitMQ (optional, for queue-based training)

## 🛠️ Quick Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

### 3. Environment Variables

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Database Configuration  
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=chatbot-docs

# RabbitMQ Configuration (Optional)
RABBITMQ_URL=amqps://username:password@host.cloudamqp.com/vhost
QUEUE_NAME=training_tasks

# Training Configuration
DOCS_ROOT_DIR=./chatbot-docs/content
```

### 4. Start Qdrant Database

```bash
# Using Docker (recommended)
docker run -p 6333:6333 qdrant/qdrant

# Or install locally - see Qdrant documentation
```

## 🚀 Usage

### Basic File Training

Process documents from your content directory:

```bash
source venv/bin/activate
python3 training-job-gemini.py
```

### Queue-Based Training

#### Send Test Content
```bash
python3 manage_queue.py send
```

#### Send Custom Content  
```bash
python3 manage_queue.py custom
```

#### Monitor Queue
```bash
python3 manage_queue.py status
```

#### Reset Queue
```bash
python3 manage_queue.py reset
```

#### Interactive Mode
```bash
python3 manage_queue.py
```

## 📖 Training Modes

### Mode 1: File-Based Training

Processes files from the `DOCS_ROOT_DIR` directory:
- Automatically scans for markdown, text, and other supported formats
- Splits documents into optimal chunks
- Creates embeddings for each chunk
- Stores in Qdrant with metadata

### Mode 2: Queue-Based Training  

Real-time content processing via RabbitMQ:
- Receives content through message queue
- Processes content directly without file I/O
- Supports both content and file path messages
- Enables dynamic training without restarts

## 🔄 Message Formats

### Content-Based Message (Recommended)

Send content directly for immediate processing:

```json
{
    "content": "Your text content here...",
    "document_id": "unique_identifier", 
    "source": "content_source",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### File-Based Message (Legacy Support)

Reference files to be processed:

```json
{
    "file_path": "document.md",
    "source": "file_system",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Core Components

### `training-job-gemini.py`
Main training script with dual-phase operation:
- **Phase 1**: Processes default files from content directory
- **Phase 2**: Listens for queue messages and processes them

Key functions:
- `train_default_files()`: Process files from root directory
- `process_file()`: Process individual files
- `process_content_directly()`: Process content from queue messages
- `get_embedding()`: Create embeddings using Gemini API

### `manage_queue.py`
Queue management utility for RabbitMQ operations:
- Send test and custom messages
- Monitor queue status
- Reset queue state
- Interactive queue management

### `test-gemini-api.py`
API connectivity testing utility

## 🐳 Docker Support

### Build Training Container
```bash
docker build -t ai-chatbot-training .
```

### Run with Environment File
```bash
docker run --env-file .env ai-chatbot-training
```

## 🔍 Troubleshooting

### Common Issues

**Qdrant Connection Failed**
```bash
# Start Qdrant using Docker
docker run -p 6333:6333 qdrant/qdrant

# Check if port 6333 is accessible
curl http://localhost:6333/collections
```

**RabbitMQ SSL Issues**
```bash
# Verify CloudAMQP URL format
# Should be: amqps://username:password@host.cloudamqp.com/vhost

# Test connection
python3 manage_queue.py status
```

**Queue Declaration Errors**
```bash
# Reset problematic queue
python3 manage_queue.py reset
```

**Gemini API Issues**
```bash
# Test API key
python3 test-gemini-api.py

# Check API quota and billing
```

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=1
python3 training-job-gemini.py
```

## 📊 Performance Optimization

### Chunking Strategy
Adjust text splitting parameters in the code:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # Increase for longer contexts
    chunk_overlap=200   # Adjust overlap for continuity
)
```

### Batch Processing
Process multiple documents efficiently:
- Queue multiple messages for batch processing
- Use connection pooling for database operations
- Implement prefetch for queue consumers

### Monitoring
The system provides comprehensive logging:
- Training progress with chunk counts
- Queue processing status
- Vector database operations
- Error tracking and recovery

## 🛡️ Security

- **Environment Variables**: All sensitive data in `.env` files
- **SSL/TLS**: Secure connections to CloudAMQP
- **Input Validation**: Sanitized content processing
- **Error Handling**: No sensitive data in error messages

## 🤝 API Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |
| `QDRANT_URL` | Qdrant database URL | `http://localhost:6333` | ✅ |
| `QDRANT_COLLECTION` | Vector collection name | `chatbot-docs` | ✅ |
| `RABBITMQ_URL` | RabbitMQ connection URL | - | ❌ |
| `QUEUE_NAME` | Queue name for tasks | `training_tasks` | ❌ |
| `DOCS_ROOT_DIR` | Default files directory | `../content` | ❌ |

### Command Line Interface

```bash
# Training Commands
python3 training-job-gemini.py              # Start training system
python3 test-gemini-api.py                  # Test API connection

# Queue Management Commands  
python3 manage_queue.py status              # Check queue status
python3 manage_queue.py send                # Send test message
python3 manage_queue.py custom              # Send custom content
python3 manage_queue.py reset               # Reset queue
python3 manage_queue.py                     # Interactive mode
```

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Google Gemini API Guide](https://ai.google.dev/docs)
- [RabbitMQ Python Tutorial](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)
- [CloudAMQP Setup Guide](https://www.cloudamqp.com/docs/index.html)

## 🐛 Contributing

1. Follow PEP 8 style guidelines
2. Add comprehensive tests for new features
3. Update documentation for changes
4. Submit pull requests with clear descriptions

---

**Part of the AI Chatbot Vector Search project** | [Main Repository](../README.md)
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
mkdir -p ./chatbot-docs/content

# Add your documents to the content directory
# Supported formats: .md, .txt, .pdf
```

Example structure:
```
./chatbot-docs/
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
ls -la ./chatbot-docs/content/

# Verify file permissions
chmod 644 ./chatbot-docs/content/*.md
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
