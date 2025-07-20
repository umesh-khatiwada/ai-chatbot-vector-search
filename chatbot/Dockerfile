FROM python:3.12-slim-bookworm

# Set environment variables for Docker
ENV QDRANT_URL=http://qdrant-database:6333
ENV COLLECTION_NAME=chatbot-docs
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt update && \
    apt install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the streamlit app
CMD ["streamlit", "run", "chat-gemini.py", "--server.port=8501", "--server.address=0.0.0.0"]

