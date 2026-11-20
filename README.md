# AI Chatbot Vector Search

A Streamlit chatbot that answers questions from your own documents using Google Gemini embeddings, a Qdrant vector database and an optional RabbitMQ ingestion queue.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)
![Qdrant](https://img.shields.io/badge/vector%20db-Qdrant-DC244C)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

The repository has two parts:

- **`training/`** reads Markdown/text documents (or messages from a RabbitMQ queue), splits them into chunks, creates embeddings with the Gemini API and stores them in Qdrant.
- **`chatbot/`** is a Streamlit app that embeds each user question, runs a similarity search in Qdrant, and sends the retrieved context plus the conversation history to a Gemini model to produce the answer.

## Features

- Document training from `.md` and `.txt` files (`training/training-job-gemini.py`).
- Queue-based training through RabbitMQ, with a helper CLI to inspect and feed the queue (`training/manage_queue.py`).
- Streamlit chat UI with conversation memory, a model selector (`gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`) and source display (`chatbot/chat-gemini.py`).
- Gemini `models/text-embedding-004` embeddings stored in Qdrant.
- System validation script that checks environment, Gemini, Qdrant and RabbitMQ (`training/validate_system.py`).
- Dockerfiles for both components and Kubernetes manifests for Qdrant, the chatbot and the training job.

## Architecture

```mermaid
graph TB
    subgraph Ingestion
        F[Markdown / text files] --> T[training-job-gemini.py]
        Q[RabbitMQ queue] --> T
        T -->|text-embedding-004| G1[Gemini API]
        T -->|upsert vectors| D[(Qdrant)]
    end
    subgraph Chat
        U[User] --> S[Streamlit chat-gemini.py]
        S -->|embed query| G1
        S -->|similarity search| D
        S -->|context + history| G2[Gemini chat model]
        G2 --> S
    end
```

## Prerequisites

- Python 3.8+ (`setup.sh` enforces this; the Docker images use Python 3.12 for the chatbot and 3.10 for training)
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/app/apikey))
- A running Qdrant instance (local Docker, Kubernetes or Qdrant Cloud)
- RabbitMQ (optional, only for queue-based training)
- Docker and `kubectl` (optional)

## Quick Start

```bash
git clone https://github.com/umesh-khatiwada/ai-chatbot-vector-search.git
cd ai-chatbot-vector-search

# 1. Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 2. Train from the sample docs
cd training
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env, see Configuration
python3 validate_system.py  # optional sanity check
python3 training-job-gemini.py

# 3. Run the chatbot
cd ../chatbot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env
streamlit run chat-gemini.py
```

Streamlit serves the UI on http://localhost:8501 by default. `setup.sh` in the repository root automates the training environment setup.

## Configuration

Copy `.env.example` to `.env` in each component directory and fill in your own values. Never commit real keys.

| Variable | Used by | Description | Default |
|----------|---------|-------------|---------|
| `GEMINI_API_KEY` | training, chatbot | Google Gemini API key | required |
| `QDRANT_URL` | training, chatbot | Qdrant endpoint | `http://localhost:6333` |
| `APIKEY` | training, chatbot | Qdrant API key (only for secured/cloud Qdrant) | none |
| `COLLECTION_NAME` | chatbot | Qdrant collection to search | `chatbot-docs` |
| `QDRANT_COLLECTION` | training | Qdrant collection to write to | `chatbot-docs` |
| `AI_MODEL` | chatbot | Gemini chat model | `gemini-pro` |
| `APP_TITLE` | chatbot | Page title | `AI Chatbot with Vector Search` |
| `APP_CONTENT` | chatbot | Welcome message | built-in text |
| `RABBITMQ_URL` | training | AMQP connection URL | `amqp://guest:guest@localhost:5672/` |
| `QUEUE_NAME` | training | Queue to consume | `embedding_tasks` (training job), `test` (`manage_queue.py`) |
| `DOCS_ROOT_DIR` | training | Directory with `.md`/`.txt` files | `./chatbot-docs/content` |

Note: the collection variable is named `COLLECTION_NAME` in the chatbot but `QDRANT_COLLECTION` in the training job. Keep both pointing at the same collection. `TEXT_EMBED` appears in `.env.example` files and manifests but is only read by the legacy `chatbot/chat.py`.

## Usage

### Training

```bash
cd training
python3 training-job-gemini.py          # file and/or queue based training
```

Place `.md` or `.txt` files under `DOCS_ROOT_DIR`. A sample is provided in `training/chatbot-docs/content/faq.md`.

### Queue management

```bash
python3 manage_queue.py status    # inspect the queue
python3 manage_queue.py send      # send a test message
python3 manage_queue.py custom    # send custom content
python3 manage_queue.py create    # create a fresh queue
python3 manage_queue.py reset     # reset the queue
python3 manage_queue.py delete    # delete the queue
python3 manage_queue.py           # interactive menu
```

### Other utilities

```bash
python3 test-gemini-api.py   # check the Gemini API key
python3 validate_system.py   # check env, Gemini, Qdrant and RabbitMQ
```

Function-level reference for the training scripts is in [docs/API.md](docs/API.md).

### Docker

```bash
# Training job
cd training && docker build -t ai-chatbot-training . && docker run --env-file .env ai-chatbot-training

# Chatbot (the image exposes 8501)
cd chatbot && docker build -t ai-chatbot-app . && docker run --env-file .env -p 8501:8501 ai-chatbot-app
```

### Kubernetes

`manifests/` contains `qdrant-deployment.yaml`, `chatbot-deployment.yaml`, `chatbot-tranining.yaml` and `ingress-class.yaml`. They reference prebuilt images from Docker Hub and set configuration as inline `env` values; replace these with Kubernetes Secrets before using them for anything real.

## Project Structure

```
ai-chatbot-vector-search/
├── chatbot/
│   ├── chat-gemini.py        # Streamlit app using Gemini (used by the Dockerfile)
│   ├── chat.py               # Earlier Vertex AI based version
│   ├── styles.py             # UI styling
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── training/
│   ├── training-job-gemini.py  # Embedding + ingestion job
│   ├── manage_queue.py         # RabbitMQ helper CLI
│   ├── validate_system.py      # Environment/service checks
│   ├── test-gemini-api.py      # Gemini API check
│   ├── chatbot-docs/content/faq.md
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── manifests/                # Kubernetes manifests
├── docs/API.md               # Training function reference
├── setup.sh                  # Training environment bootstrap
├── CONTRIBUTING.md
└── LICENSE
```

## Development

There is no automated test suite. Use `training/validate_system.py` and `training/test-gemini-api.py` for smoke checks. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Roadmap

- [ ] Web UI for queue management
- [ ] Batch processing support
- [ ] Multiple embedding models
- [ ] Advanced search filters
- [ ] REST API endpoints
- [ ] Monitoring dashboard

## License

Released under the [MIT License](LICENSE).

## Author

Umesh Khatiwada - [github.com/umesh-khatiwada](https://github.com/umesh-khatiwada)
