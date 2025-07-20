# 🤖 Chatbot with Vector Search

A sophisticated chatbot application built with Streamlit, LangChain, and Google Vertex AI that uses vector search to provide context-aware responses. The system consists of two main components: a training pipeline for document embedding and a chat interface for user interactions.

## 🏗️ Architecture

- **Chatbot Interface**: Streamlit-based web application with conversation memory
- **Vector Search**: Qdrant database for semantic document retrieval
- **AI Model**: Google Vertex AI (Gemini Pro) for response generation
- **Document Processing**: Training pipeline for embedding documents into vector space

## 📋 Prerequisites

- Python 3.12+
- Google Cloud Platform account with Vertex AI enabled
- Qdrant database (local or cloud instance)
- Valid GCP credentials

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/umesh-khatiwada/chatbot.git
cd chatbot
```

### 2. Create and Activate Virtual Environment

#### Using venv (recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### Using conda

```bash
# Create conda environment
conda create -n chatbot python=3.12

# Activate environment
conda activate chatbot
```

### 3. Install Dependencies

#### For Chatbot Application

```bash
cd chatbot
pip install -r requirements.txt
```

#### For Training Pipeline

```bash
cd training
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Authentication

```bash
# Install Google Cloud CLI if not already installed
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory or set the following environment variables:

```bash
# Required
QDRANT_URL=http://localhost:6333  # Your Qdrant instance URL
APIKEY=your_qdrant_api_key        # Qdrant API key (if required)
COLLECTION_NAME=chatbot-docs      # Qdrant collection name

# Optional (defaults will be used if not set)
AI_MODEL=gemini-pro              # Vertex AI model name
TEXT_EMBED=text-embedding-005    # Embedding model
APP_TITLE=🤖 Chatbot             # Application title
APP_CONTENT=Welcome! How can I help you?  # Welcome message
```

### Qdrant Database Setup

#### Option 1: Local Qdrant (Development)

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant:latest

# Using Docker Compose
docker-compose up -d
```

#### Option 2: Qdrant Cloud

1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create a cluster
3. Get your cluster URL and API key
4. Update the environment variables

## 📊 Training Data

### 1. Prepare Your Documents

Place your training documents in the appropriate directory. The training script supports:
- Markdown files (.md)
- PDF files (.pdf)  
- Text files (.txt)

### 2. Update Training Configuration

Edit `training/training-job-chatbot.py`:

```python
# Update file paths to your documents
file_paths = (
    "content/your-doc1.md",
    "content/your-doc2.md",
    "content/your-doc3.md"
)

# Update root directory path
root_dir = "/path/to/your/documents/"

# Update Qdrant configuration
collection_name = "your-collection-name"
url = "your-qdrant-url"
```

### 3. Run Training Pipeline

```bash
cd training
python training-job-chatbot.py
```

## 🚀 Running the Application

### Local Development

```bash
cd chatbot
streamlit run chat.py
```

The application will be available at `http://localhost:8501`

### Using Docker

```bash
# Build the Docker image
docker build -t chatbot-app ./chatbot

# Run the container
docker run -p 8501:8501 \
  -e QDRANT_URL=your_qdrant_url \
  -e APIKEY=your_api_key \
  -e COLLECTION_NAME=your_collection \
  chatbot-app
```

## 📝 Usage

1. **Start the Application**: Run the Streamlit app using one of the methods above
2. **Ask Questions**: Type your questions in the chat input
3. **Get Responses**: The chatbot will search relevant documents and provide context-aware answers
4. **Conversation Memory**: The app maintains conversation history for better context

## 🔧 Features

- **Vector Search**: Semantic search through your document collection
- **Conversation Memory**: Maintains context across multiple exchanges
- **Streaming Responses**: Real-time response generation
- **Customizable UI**: Configurable title and welcome message
- **Docker Support**: Easy deployment with containerization
- **Multiple Document Types**: Support for PDF, Markdown, and text files

## 📁 Project Structure

```
chatbot/
├── README.md
├── chatbot/
│   ├── chat.py              # Main Streamlit application
│   ├── Dockerfile           # Docker configuration
│   └── requirements.txt     # Python dependencies
└── training/
    ├── training-job-chatbot.py  # Document embedding pipeline
    └── requirements.txt         # Training dependencies
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Re-authenticate with Google Cloud
   gcloud auth application-default login
   ```

2. **Qdrant Connection Error**
   - Verify Qdrant is running and accessible
   - Check the `QDRANT_URL` environment variable
   - Ensure API key is correct (if using Qdrant Cloud)

3. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Memory Issues**
   - Reduce chunk size in training script
   - Process fewer documents at once
   - Increase system memory allocation

### Logs and Debugging

```bash
# Run with verbose logging
streamlit run chat.py --logger.level=debug

# Check Qdrant logs
docker logs qdrant-container-name
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Check existing issues before creating new ones
- Provide detailed information including error messages and environment details

## 🔮 Roadmap

- [ ] Support for more document formats
- [ ] Advanced conversation analytics
- [ ] Multi-language support
- [ ] Custom embedding models
- [ ] API endpoint for programmatic access
