# 🤖 AI Chatbot Application

An enhanced Streamlit-based chatbot interface that uses Google Gemini API and Qdrant vector database for intelligent, context-aware conversations.

## ✨ Features

- 🎨 **Modern UI** with real-time status indicators
- 🔍 **Vector Search** with relevance scoring
- ⚙️ **Dynamic Configuration** via sidebar
- 📊 **Session Statistics** and performance metrics
- 🔄 **Multiple AI Models** (Gemini Pro, Flash, 1.5-Pro)
- 💬 **Conversation Memory** with context preservation

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Qdrant database running (see setup below)

### 2. Install Dependencies

```bash
# Make sure you're in the chatbot directory
cd chatbot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install streamlit google-generativeai qdrant-client langchain python-dotenv
```

### 3. Set Up Environment

Create a `.env` file in this directory:

```bash
# Gemini API Key (required)
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=chatbot-docs

# Optional Customizations
APP_TITLE=🤖 My AI Assistant
APP_CONTENT=Welcome! How can I help you with your documents?
AI_MODEL=gemini-1.5-flash
```

### 4. Start Qdrant Database

```bash
# Using Docker (recommended)
docker run -d -p 6333:6333 --name qdrant-local qdrant/qdrant:latest

# Verify it's running
curl http://localhost:6333/health
```

### 5. Prepare Training Data

Make sure you have documents embedded in Qdrant. If not, run the training pipeline first:

```bash
cd ../training
python3 training-job-gemini.py
cd ../chatbot
```

### 6. Launch the Chatbot

```bash
streamlit run chat-gemini.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Available Scripts

| Script | Description |
|--------|-------------|
| `chat-gemini.py` | Enhanced chatbot with Gemini API |
| `chat.py` | Original Vertex AI version |

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `QDRANT_URL` | Qdrant database URL | `http://localhost:6333` |
| `COLLECTION_NAME` | Vector collection name | `chatbot-docs` |
| `APP_TITLE` | Application title | `🤖 AI Chatbot` |
| `APP_CONTENT` | Welcome message | Default welcome |
| `AI_MODEL` | Gemini model to use | `gemini-pro` |

### Sidebar Controls

- **AI Model**: Switch between Gemini models
- **Search Results**: Adjust number of retrieved documents (1-10)
- **Response Creativity**: Control response randomness (0.0-1.0)
- **Clear Chat**: Reset conversation history

## 🎯 Usage Tips

### Getting Better Results

1. **Ask Specific Questions**: "What is vector search?" vs "Tell me about search"
2. **Reference Context**: "Based on the FAQ, how do I..."
3. **Use Keywords**: Include terms that appear in your documents
4. **Check Status**: Ensure green indicators in sidebar

### Understanding Responses

- 🟢 **High Confidence** (>0.7): Very relevant sources found
- 🟡 **Moderate Confidence** (0.5-0.7): Somewhat relevant sources
- 🔴 **Low Confidence** (<0.5): Limited relevant information

## 🐛 Troubleshooting

### Common Issues

#### 🔴 API Connection Failed
```bash
# Test your API key
python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
print('API key works!')
"
```

#### 🔴 Qdrant Connection Failed
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart if needed
docker restart qdrant-local

# Check logs
docker logs qdrant-local
```

#### 📄 No Search Results
1. Verify collection exists:
   ```bash
   curl http://localhost:6333/collections/chatbot-docs
   ```
2. Run training pipeline to add documents
3. Check document content and format

#### 🐌 Slow Performance
- Reduce search results count (sidebar)
- Switch to `gemini-1.5-flash` model
- Ensure good internet connection
- Check Qdrant performance

### Debug Mode

```bash
# Run with debug logging
streamlit run chat-gemini.py --logger.level=debug

# Check Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log
```

## 🔧 Advanced Configuration

### Custom Styling

Edit CSS in `chat-gemini.py`:

```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #your-color 0%, #another-color 100%);
    }
</style>
""", unsafe_allow_html=True)
```

### Adding New Models

Update the model options in the sidebar:

```python
model_options = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash", "your-custom-model"]
```

## 🚀 Deployment

### Local Development
```bash
streamlit run chat-gemini.py --server.port 8501
```

### Docker Deployment
```bash
# Build image
docker build -t ai-chatbot .

# Run container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  -e QDRANT_URL=your_qdrant_url \
  ai-chatbot
```

### Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets in dashboard

## 📊 Performance Metrics

- **Response Time**: 2-5 seconds typical
- **Memory Usage**: ~200MB base + conversation history
- **Concurrent Users**: 10-20 (single instance)
- **API Rate Limits**: Gemini free tier limits apply

## 🔒 Security Notes

- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ Rotate API keys regularly
- ⚠️ Consider rate limiting in production
- ⚠️ Validate user inputs

## 📞 Support

- **Issues**: Check the main repository issues
- **Documentation**: See root README for complete guide
- **API Issues**: [Google AI Studio Support](https://aistudio.google.com/app/help)
- **Qdrant Issues**: [Qdrant Documentation](https://qdrant.tech/documentation/)

## 🔗 Related Files

- `../training/` - Document processing pipeline
- `../README.md` - Complete project documentation
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
