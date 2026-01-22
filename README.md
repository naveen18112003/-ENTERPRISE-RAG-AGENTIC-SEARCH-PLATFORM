# ENTERPRISE RAG + AGENTIC SEARCH PLATFORM

An advanced enterprise-grade search platform combining **Retrieval-Augmented Generation (RAG)** with **Agentic Search** capabilities. Features dual search modes, in-memory vector store, and a modern web interface.

## 🚀 Key Features

### Dual Search Modes
- **Simple RAG Mode**: Fast, direct retrieval and answer generation
- **Agentic Search Mode**: Intelligent orchestration with:
  - Intent detection (lookup, compare, summarize, analyze)
  - Execution planning and strategy
  - Tool selection and invocation
  - Post-processing and evidence extraction
  - Full action tracking and transparency

### Technical Stack
- **Backend**: FastAPI (Python)
- **Vector Store**: NumPy-based cosine similarity search (in-memory)
- **LLM**: GPT-4o via GitHub Models or OpenAI
- **Embeddings**: text-embedding-3-small
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## 📦 Quick Start

### Prerequisites
- Python 3.9+
- Git

### Installation

```bash
git clone <repository-url>
cd -ENTERPRISE-RAG-AGENTIC-SEARCH-PLATFORM

python -m venv .venv
.\.venv\Scripts\Activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with one of the following:

**Option A: OpenAI API Key (Recommended)**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Option B: GitHub Token (Free, 50 requests/day)**
```bash
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Running the Application

**Terminal 1 - Backend (Port 8001):**
```bash
.\.venv\Scripts\Activate
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8001
```

**Terminal 2 - Frontend (Port 8080):**
```bash
cd public
python -m http.server 8080
```

**Access the app:** http://127.0.0.1:8080

## 📝 Usage

### 1. Upload Documents
- Click the upload icon (📎)
- Select `.txt` or `.pdf` files
- Documents are indexed immediately (in-memory, ephemeral)

### 2. Query the System

**Simple RAG Mode** - Fast lookups:
- "What is the refund policy?"
- "How many days to return an item?"

**Agentic Mode** - Complex queries:
- "Compare refund policy and cancellation policy"
- "Analyze the refund requirements"
- "Summarize the shipping policy"

## 🏗️ Architecture

```
Frontend (public/)
    ↓
API Layer (api/index.py)
    ├── /search (RAG + Agentic)
    ├── /upload (Document ingestion)
    └── / (Health check)
    ↓
RAG Engine (src/rag_engine.py)
    ├── In-memory vector store
    ├── Retrieval via cosine similarity
    └── Answer generation
```

### Architecture Difference

**Simple RAG**: `rag_engine.generate_answer()` - Direct retrieval + generation

**Agentic Search**: `rag_engine.query()` as a tool → Intent detection → Planning → Execution → Post-processing

See [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md) for detailed documentation.

## 🔌 API Endpoints

### `POST /search`
Unified search endpoint with mode selection.

**Request:**
```json
{
  "query": "Compare refund and cancellation policies",
  "mode": "agentic"  
}
```

**Response (Agentic):**
```json
{
  "mode": "agentic",
  "intent": "compare",
  "agent_plan": {
    "strategy": "Split query into components...",
    "search_queries": ["refund policy", "cancellation policy"]
  },
  "actions_taken": [...],
  "answer": "...",
  "evidence": [...],
  "sources": ["refund_policy.pdf"],
  "confidence": 0.85
}
```

### `POST /upload`
Upload and ingest documents (PDF/TXT).

**Response:**
```json
{
  "message": "Successfully processed filename.pdf. Added 15 chunks to knowledge base.",
  "filename": "filename.pdf",
  "chunks": 15
}
```

## 🛠️ Troubleshooting

### Rate Limit Errors
**Problem**: "API Rate Limit Exceeded" with GitHub Token

**Solution**: Switch to OpenAI API key
1. Get key from [platform.openai.com](https://platform.openai.com)
2. Add `OPENAI_API_KEY=sk-...` to `.env`
3. Restart backend

### Connection Errors
- Ensure backend runs on port **8001**
- Frontend should be at `http://127.0.0.1:8080`
- Check both terminals are active

## 📁 Project Structure

```
.
├── api/
│   └── index.py                    # FastAPI application & endpoints
├── backend/
│   └── app/
│       ├── controllers/
│       │   └── search_controller.py # Request routing
│       └── services/
│           ├── agentic_search.py    # Agentic pipeline
│           └── llm.py               # LLM client
├── src/
│   ├── rag_engine.py               # Core RAG engine
│   ├── chunker.py                  # Text chunking
│   ├── ingest.py                   # Document ingestion
│   └── llm_client.py               # LLM wrapper
├── public/
│   ├── index.html                  # Frontend UI
│   ├── script.js                   # Frontend logic
│   └── style.css                   # Styling
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
└── README.md                       # This file
```

## 🚀 Deployment

### Vercel

```bash
npm i -g vercel
vercel --prod
```

**Environment Variables** (Vercel Dashboard):
- Add `GITHUB_TOKEN` or `OPENAI_API_KEY`

**Important Notes**:
- 10-second timeout limit
- In-memory storage (ephemeral)
- Upload smaller files (<20 pages)

## 📚 Documentation

- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Simplified setup guide
- [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md) - Architecture details
- [GETTING_STARTED.md](GETTING_STARTED.md) - Comprehensive guide

## 🎯 Future Roadmap

- Persistent storage (Redis/Pinecone)
- Background processing for large documents
- Multi-modal support (images, tables)
- User authentication & access control
- Query analytics & monitoring
- Export conversations

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
