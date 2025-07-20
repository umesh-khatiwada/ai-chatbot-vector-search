# API Documentation

## Training System API

### Core Training Functions

#### `training-job-gemini.py`

##### `get_embedding(text: str) -> List[float] | None`
Creates text embeddings using Google Gemini API.

**Parameters:**
- `text` (str): Input text to create embeddings for

**Returns:**
- `List[float]`: 768-dimensional embedding vector
- `None`: If embedding creation fails

**Example:**
```python
embedding = get_embedding("Sample text content")
if embedding:
    print(f"Created {len(embedding)}-dimensional embedding")
```

##### `process_file(file_path: str, docs_count: int = 0) -> int`
Process a single file and create vector embeddings.

**Parameters:**
- `file_path` (str): Path to the file relative to `ROOT_DIR`
- `docs_count` (int, optional): Starting count for document IDs

**Returns:**
- `int`: Number of document chunks created

**Example:**
```python
chunks_created = process_file("faq.md", 0)
print(f"Created {chunks_created} chunks")
```

##### `process_content_directly(content: str, document_id: str, source: str, docs_count: int = 0) -> int`
Process content directly from memory without file I/O.

**Parameters:**
- `content` (str): Text content to process
- `document_id` (str): Unique identifier for the document
- `source` (str): Source system identifier
- `docs_count` (int, optional): Starting count for document IDs

**Returns:**
- `int`: Number of document chunks created

**Example:**
```python
content = "Your document content here..."
chunks = process_content_directly(content, "doc_001", "api", 0)
```

##### `train_default_files() -> int`
Train from files in the default root directory.

**Returns:**
- `int`: Total number of document chunks processed

**Example:**
```python
total_chunks = train_default_files()
print(f"Processed {total_chunks} total chunks")
```

##### `start_worker()`
Main worker function that runs dual-phase training.

**Phases:**
1. **Default File Training**: Processes files from `DOCS_ROOT_DIR`
2. **Queue Listener**: Listens for RabbitMQ messages

**Example:**
```python
# This runs indefinitely until interrupted
start_worker()
```

### Queue Management API

#### `manage_queue.py`

##### `create_ssl_connection() -> pika.BlockingConnection | None`
Create SSL connection to CloudAMQP.

**Returns:**
- `pika.BlockingConnection`: Active connection object
- `None`: If connection fails

##### `send_test_message() -> bool`
Send a pre-built test message to the queue.

**Returns:**
- `bool`: True if successful, False otherwise

##### `send_custom_content() -> bool`
Interactive function to send custom content to the queue.

**Returns:**
- `bool`: True if successful, False otherwise

##### `check_queue_status() -> bool`
Check current queue status and message count.

**Returns:**
- `bool`: True if successful, False otherwise

##### `reset_queue() -> bool`
Delete and recreate the queue.

**Returns:**
- `bool`: True if successful, False otherwise

## Message Queue API

### Message Formats

#### Content-Based Message
Used for direct content processing without file I/O.

```json
{
    "content": "Your text content here...",
    "document_id": "unique_identifier",
    "source": "source_name",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Fields:**
- `content` (string, required): The actual text content to process
- `document_id` (string, required): Unique identifier for the document
- `source` (string, required): Source system or identifier
- `timestamp` (string, optional): ISO 8601 timestamp

#### File-Based Message
Used for processing files from the filesystem.

```json
{
    "file_path": "document.md",
    "source": "file_system",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Fields:**
- `file_path` (string, required): Path to file relative to `DOCS_ROOT_DIR`
- `source` (string, required): Source system identifier
- `timestamp` (string, optional): ISO 8601 timestamp

### Queue Operations

#### Send Message
```python
import json
import pika

# Create connection
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()

# Prepare message
message = {
    "content": "Sample content",
    "document_id": "doc_001",
    "source": "api"
}

# Send message
channel.basic_publish(
    exchange='',
    routing_key=QUEUE_NAME,
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2)  # Persistent
)
```

#### Consumer Callback
```python
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        # Process message
        if "content" in data:
            # Handle content-based message
            process_content_directly(
                data["content"],
                data["document_id"],
                data["source"]
            )
        else:
            # Handle file-based message
            process_file(data["file_path"])
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Reject and requeue on error
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `QDRANT_URL` | Qdrant database URL | `http://localhost:6333` |
| `QDRANT_COLLECTION` | Vector collection name | `chatbot-docs` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_URL` | RabbitMQ connection URL | `amqp://guest:guest@localhost:5672/` |
| `QUEUE_NAME` | Queue name for training tasks | `test` |
| `DOCS_ROOT_DIR` | Default files directory | `../chatbot-docs/content` |

### SSL Configuration

For CloudAMQP connections, SSL is automatically configured:

```python
if parsed_url.scheme == 'amqps':
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    params.ssl_options = pika.SSLOptions(ssl_context)
```

## Error Handling

### Common Exceptions

#### `ConnectionError`
Raised when unable to connect to external services.

```python
try:
    client = QdrantClient(url=QDRANT_URL)
except ConnectionError as e:
    print(f"Failed to connect to Qdrant: {e}")
```

#### `json.JSONDecodeError`
Raised when queue message is not valid JSON.

```python
try:
    data = json.loads(body)
except json.JSONDecodeError as e:
    print(f"Invalid JSON in message: {e}")
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

#### `pika.exceptions.ChannelClosedByBroker`
Raised when RabbitMQ channel is closed by broker.

```python
try:
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
except pika.exceptions.ChannelClosedByBroker as e:
    print(f"Channel closed by broker: {e}")
    # Recreate channel
    channel = connection.channel()
```

### Retry Strategies

#### Exponential Backoff
```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

## Performance Considerations

### Chunking Strategy
- **Chunk Size**: 1000 characters (adjustable)
- **Overlap**: 200 characters (maintains context)
- **Splitting**: Recursive character text splitter

### Embedding Batch Processing
- Process embeddings one at a time to avoid rate limits
- Consider implementing batch processing for high-volume scenarios

### Vector Storage
- Use batch upserts for multiple vectors
- Configure appropriate collection parameters

```python
# Batch upsert example
points = [
    PointStruct(id=i, vector=embedding, payload=metadata)
    for i, (embedding, metadata) in enumerate(data)
]
client.upsert(collection_name=COLLECTION_NAME, points=points)
```

## Security Best Practices

### API Key Management
- Store API keys in environment variables
- Never commit API keys to version control
- Use different keys for development and production

### SSL/TLS Configuration
- Use SSL for all external connections
- Verify certificates in production environments
- Configure appropriate cipher suites

### Input Validation
- Validate all queue message content
- Sanitize file paths to prevent directory traversal
- Limit content size to prevent memory issues

## Monitoring and Logging

### Standard Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Processing started")
```

### Metrics Collection
- Track processing time per document
- Monitor queue depth and processing rate
- Log embedding creation success/failure rates

### Health Checks
```python
def health_check():
    """Verify system components are healthy"""
    try:
        # Check Qdrant connection
        client.get_collections()
        
        # Check Gemini API
        get_embedding("test")
        
        # Check queue connection
        create_ssl_connection()
        
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```
