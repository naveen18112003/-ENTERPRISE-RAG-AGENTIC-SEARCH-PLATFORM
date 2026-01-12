# ENTERPRISE RAG + AGENTIC SEARCH PLATFORM

## Overview

An advanced enterprise-grade search platform that combines **Retrieval-Augmented Generation (RAG)** with **Agentic Search** capabilities. This system provides two distinct modes for answering questions about company policies and documents:

1. **Simple RAG Mode**: Direct retrieval and answer generation
2. **Agentic Search Mode**: True agentic pipeline with intent detection, planning, tool selection, and post-processing

The platform uses an **In-Memory Vector Store** optimized for serverless deployment and provides a professional, modern web interface for document upload and querying.

---

## Key Features

### 🚀 Dual Search Modes
- **Simple RAG Mode**: Fast, direct retrieval and answer generation
- **Agentic Search Mode**: Intelligent orchestration with:
  - Intent detection (lookup, compare, summarize, analyze)
  - Execution planning and strategy
  - Tool selection and invocation
  - Post-processing and evidence extraction
  - Full action tracking and transparency

### 🏗️ Architecture
- **Serverless-Ready**: Built with FastAPI, optimized for Vercel deployment
- **In-Memory Vector Store**: Lightweight, no external vector DB dependencies
- **Modular Design**: Clean separation between RAG engine and agentic orchestration
- **Professional UI**: Modern, responsive interface with mode switching

### 🔧 Technical Stack
- **Backend**: FastAPI (Python)
- **Vector Store**: NumPy-based cosine similarity search
- **LLM**: GPT-4o via GitHub Models (Azure-backed)
- **Embeddings**: text-embedding-3-small
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (public/)                    │
│  - Modern UI with mode selector                         │
│  - Document upload interface                            │
│  - Chat interface                                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   API Layer (api/)                       │
│  - /health: Health check                                │
│  - /upload: Document ingestion                          │
│  - /query: Simple RAG endpoint                          │
│  - /search: Unified endpoint (RAG + Agentic)            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│  Simple RAG    │      │  Agentic Search    │
│  (Direct)      │      │  (Orchestrated)    │
└───────┬────────┘      └─────────┬──────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────┐
        │   RAG Engine (src/)   │
        │  - Vector storage     │
        │  - Retrieval          │
        │  - Generation         │
        └───────────────────────┘
```

### Backend Structure

```
backend/
├── app/
│   ├── controllers/
│   │   └── search_controller.py    # Routes requests to RAG/Agentic
│   └── services/
│       └── agentic_search.py       # Agentic pipeline implementation
api/
└── index.py                        # FastAPI application & endpoints

src/
├── rag_engine.py                   # Core RAG functionality
├── chunker.py                      # Text chunking utilities
├── ingest.py                       # Document ingestion
└── llm_client.py                   # LLM client wrapper
```

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.9+**
- **Git**
- A terminal (PowerShell, Command Prompt, or Bash)

### 2. Installation

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd "Enterprise RAG + Agentic Search Platform"

# Create a virtual environment (Optional but Recommended)
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate
# Mac/Linux:
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Configuration (Critical Step)

1.  Create a file named `.env` in the project root.
2.  Add **ONE** of the following tokens:

**Option A: OpenAI API Key (Recommended)**
*Best for reliability and avoiding rate limits.*
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Option B: GitHub Token (Free)**
*Good for testing, but limited to 50 requests/day.*
```bash
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Running the Application

You need to run the **Backend** and **Frontend** in separate terminals.

#### Terminal 1: Backend API
Runs on **Port 8001** (to avoid conflicts).

```bash
# Make sure your virtual env is active
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8001
```

#### Terminal 2: Frontend UI
Runs on **Port 8080**.

```bash
cd public
python -m http.server 8080
```

### 5. Access the App
Open your browser and go to:
👉 **http://127.0.0.1:8080**

The frontend will automatically connect to the backend at `http://localhost:8001`.

### 6. Quick Start Guide (Simplified)
For a straightforward, copy-paste guide on running this project, see **[HOW_TO_RUN.md](HOW_TO_RUN.md)**.

### 7. Ingestion (Adding Documents)

There are **two ways** to add documents (PDF/TXT) to the system:

#### A. Web Interface (Recommended)
1. Go to the app at `http://127.0.0.1:8080`.
2. Click the **Upload Button** (⬆️ icon).
3. Select your file. It will be indexed immediately.
   * *Note: Data is ephemeral (in-memory) and resets when you restart the backend.*

#### B. Command Line (CLI Mode)
1. Place files in the `data/` folder.
2. Run: `python main.py --ingest --query "My question"`
   * *Note: CLI ingestion does NOT update the running web server's memory.*

---

## API Endpoints

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "rag_initialized": false,
  "token_set": true,
  "documents_in_memory": 0
}
```

### POST `/upload`
Upload and ingest documents.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "message": "Processed filename.pdf. Indexed 15/15 chunks.",
  "filename": "filename.pdf",
  "chunks_total": 15,
  "chunks_indexed": 15
}
```

### POST `/query`
Simple RAG query endpoint (legacy, for backward compatibility).

**Request:**
```json
{
  "query": "What is the refund policy?"
}
```

**Response:**
```json
{
  "answer": "...",
  "sources": ["refund_policy.pdf"],
  "context": ["chunk1", "chunk2", ...]
}
```

### POST `/search`
Unified search endpoint with mode selection.

**Request:**
```json
{
  "query": "Compare refund policy and cancellation policy",
  "mode": "rag"  // or "agentic"
}
```

**Response (Simple RAG Mode):**
```json
{
  "mode": "rag",
  "answer": "...",
  "sources": ["refund_policy.pdf"],
  "context": ["chunk1", "chunk2"]
}
```

**Response (Agentic Mode):**
```json
{
  "mode": "agentic",
  "intent": "compare",
  "agent_plan": {
    "strategy": "Split query into components, retrieve relevant sections for each, then synthesize comparison",
    "search_queries": ["refund policy", "cancellation policy"],
    "tools_used": ["rag_retrieval"],
    "post_processing_method": "combine_and_compare"
  },
  "actions_taken": [
    "Detected intent: compare",
    "Created execution plan: ...",
    "Selected RAG retrieval tool",
    "Executing RAG retrieval for: 'refund policy'",
    "Retrieved 5 relevant chunks",
    "Starting post-processing: combine_and_compare"
  ],
  "answer": "...",
  "evidence": [
    {
      "source": "refund_policy.pdf",
      "excerpt": "Refunds must be requested within 30 days..."
    }
  ],
  "sources": ["refund_policy.pdf", "cancellation_policy.pdf"],
  "confidence": 0.85
}
```

---

## Usage Guide

### 1. Start the Application
Follow the setup instructions above to start both backend and frontend servers.

### 2. Upload Documents
- Click the upload icon (📎) in the input area
- Select `.txt` or `.pdf` files
- Wait for the "Indexed X/X chunks" confirmation message
- **Note**: Vercel has a 10-second timeout limit. For large files, split them into smaller chunks.

### 3. Query the System

#### Simple RAG Mode
Select "Simple RAG" mode from the header tabs, then ask questions like:
- "What is the refund policy?"
- "How many days do I have to return an item?"
- "What are the shipping options?"

**Characteristics:**
- Fast, direct answers
- Simple response format
- Best for straightforward lookups

#### Agentic Search Mode
Select "Agentic" mode from the header tabs, then try:

**Comparison Queries:**
- "Compare refund policy and cancellation policy"
- "What's the difference between standard and express shipping?"

**Analysis Queries:**
- "Analyze the refund policy requirements"
- "Explain how the cancellation process works"

**Summarization:**
- "Summarize the shipping policy"
- "Give me an overview of all return policies"

**Characteristics:**
- Intent-aware processing
- Multi-step reasoning
- Evidence extraction
- Action tracking
- Higher confidence scores with structured metadata

---

## How It Works

### Simple RAG Mode

```
User Query
    ↓
RAG Engine.generate_answer()
    ├── Vector Retrieval (semantic search)
    ├── Context Assembly
    └── LLM Generation
    ↓
Answer + Sources
```

**Key Points:**
- Single-step process
- Direct retrieval and generation
- Fast response times
- Simple architecture

### Agentic Search Mode

```
User Query
    ↓
Intent Detection (lookup/compare/summarize/analyze)
    ↓
Planning Phase
    ├── Strategy Selection
    ├── Query Decomposition (if comparison)
    └── Tool Selection
    ↓
Tool Execution
    └── RAG Engine.query() [Used as a tool, not generate_answer()]
    ↓
Post-Processing (varies by intent)
    ├── Combine results (comparisons)
    ├── Format evidence
    └── Generate structured answer
    ↓
Final Response with Metadata
    ├── Answer
    ├── Evidence
    ├── Agent Plan
    ├── Actions Taken
    └── Confidence Score
```

**Key Points:**
- Multi-phase orchestration
- RAG used as a tool (not direct answer generation)
- Intent-specific post-processing
- Full transparency with action tracking
- Structured evidence extraction

**Architectural Difference:**
- **Simple RAG**: Calls `rag_engine.generate_answer()` directly
- **Agentic**: Uses `rag_engine.query()` as a tool, then does its own post-processing

See [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md) for detailed architecture documentation.

---

## Deployment

### Vercel Deployment

The project is configured for Vercel serverless deployment.

#### 1. Install Vercel CLI
```bash
npm i -g vercel
vercel login
```

#### 2. Deploy
```bash
vercel --prod
```

#### 3. Configure Environment Variables

In Vercel Dashboard:
1. Go to **Settings** > **Environment Variables**
2. Add `GITHUB_TOKEN` with your GitHub Personal Access Token
3. Ensure no trailing newlines or spaces

#### 4. Important Notes
- **Timeout Limit**: Vercel functions have a 10-second timeout
- **Document Size**: Upload smaller files (<20 pages) or split large documents
- **Ephemeral Storage**: Documents stored in-memory (lost on serverless function sleep)
- **Auto-ingest**: Disabled on startup to prevent timeout issues

---

## Troubleshooting

### Backend Issues

**"API Rate Limit Exceeded" / "429 Rate Limit"**
- **GitHub Models Free Tier**: Limited to 50 requests per 24 hours.
- **Solution (Recommended)**: Use an OpenAI API key instead.
  1. Get a key from [platform.openai.com](https://platform.openai.com).
  2. Add `OPENAI_API_KEY=sk-...` to your `.env` file.
  3. Restart the backend.
- **Alternative**: Wait ~24 hours for the limit to reset.

**"Address already in use" / "WinError 10013"**
- Port 8000 might be blocked or used by another app.
- **Solution**: We now use **Port 8001** by default. Ensure you run the startup command with `--port 8001`.

**"Indexed 0/X chunks"**
- Embedding API may have failed.
- Check backend logs for error messages.
- Verify your token is correct in `.env`.

**Import Errors**
- Ensure you have activated your virtual environment (`.venv`).
- Run `pip install -r requirements.txt` again.

### Frontend Issues

**"Error connecting to the server"**
- Verify backend is running on **Port 8001**.
- Check that you are accessing the frontend at `http://127.0.0.1:8080`.
- Only use `localhost` (not IP) if you are in development mode.

**Mode selector not working**
- Hard refresh browser (Ctrl+F5)
- Check browser console for JavaScript errors
- Ensure `script.js` is loaded correctly

---

## Project Structure

```
Enterprise RAG + Agentic Search Platform/
├── api/
│   └── index.py                    # FastAPI application
├── backend/
│   └── app/
│       ├── controllers/
│       │   └── search_controller.py
│       └── services/
│           └── agentic_search.py
├── src/
│   ├── rag_engine.py              # Core RAG engine
│   ├── chunker.py                 # Text chunking
│   ├── ingest.py                  # Document ingestion
│   ├── llm_client.py              # LLM client
│   └── prompts.py                 # Prompt templates
├── public/
│   ├── index.html                 # Frontend UI
│   ├── script.js                  # Frontend logic
│   └── style.css                  # Styling
├── data/
│   └── *.txt, *.pdf               # Sample documents
├── requirements.txt               # Python dependencies
├── vercel.json                    # Vercel configuration
├── .env                           # Environment variables (create this)
├── README.md                      # This file
└── AGENTIC_ARCHITECTURE.md        # Architecture documentation
```

---

## Key Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **NumPy**: Vector operations and cosine similarity
- **OpenAI SDK**: LLM and embeddings via GitHub Models
- **Python 3.9+**: Core language
- **HTML5/CSS3/JavaScript**: Frontend (no framework dependencies)

---

## Future Improvements

- **Persistence**: Redis or Pinecone integration for document persistence
- **Async Processing**: Background queue for document ingestion
- **Multi-modal Support**: Image and table extraction from PDFs
- **Advanced Agentic Features**: Multi-agent collaboration, tool chaining
- **Analytics**: Query analytics and performance monitoring
- **User Authentication**: Multi-user support with document access control
- **Export Features**: Export conversations and search results

---

## License

[Your License Here]

---

## Contributing

[Your Contributing Guidelines Here]

---

## Contact

[Your Contact Information Here]
