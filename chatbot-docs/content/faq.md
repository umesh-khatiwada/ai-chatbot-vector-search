# Frequently Asked Questions

## What is this chatbot?
This chatbot is an AI-powered assistant that uses vector search to provide contextual answers based on your documentation. It's built with Streamlit, LangChain, and Google Vertex AI.

## How does it work?
The chatbot uses:
1. **Document Processing**: Your documents are split into chunks and converted into vector embeddings
2. **Vector Search**: When you ask a question, it searches for relevant document chunks using semantic similarity
3. **AI Response**: The relevant context is sent to Google's Gemini model to generate a helpful response
4. **Conversation Memory**: The system maintains conversation history for better context

## What types of documents can I use?
You can use:
- Markdown files (.md)
- PDF files (.pdf)
- Text files (.txt)

## How do I add my own documents?
1. Place your documents in the appropriate directory
2. Update the file paths in the training script
3. Run the training pipeline to create embeddings
4. The chatbot will then be able to answer questions about your documents

## Can I customize the chatbot?
Yes! You can customize:
- The welcome message
- The application title
- The AI model used
- The embedding model
- The conversation memory settings

## What do I need to get started?
- Python 3.12+
- Google Cloud account with Vertex AI enabled
- Qdrant database (local or cloud)
- Your documents for training

## Is this free to use?
The code is open source, but you'll need:
- Google Cloud credits for Vertex AI usage
- Qdrant hosting (free tier available)
- Basic compute resources for running the application
