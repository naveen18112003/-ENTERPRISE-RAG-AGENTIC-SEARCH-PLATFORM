# RAG Policy Assistant for Acme Corp

## Overview
This is a Retrieval-Augmented Generation (RAG) system designed to answer questions about Acme Corp's policies (Refund, Cancellation, Shipping) accurately and without hallucination. It uses a structured prompting strategy and an **In-Memory Vector Store** to ground answers in truth, optimized for deployment on Vercel's serverless infrastructure.

**Submission for**: AI Engineer Intern – Take-Home Assignment

## Key Features
- **Serverless Architecture**: Built with `FastAPI` and deployed on Vercel.
- **In-Memory RAG Engine**: Optimized for stateless environments (no heavy ChromaDB/Pinecone dependency).
- **GitHub Models Integration**: Uses Azure-backed usage of GPT-4o via the standard `openai` Python SDK.
- **Frontend UI**: Simple chat interface with file upload capabilities.
- **Robust Error Handling**: Includes full traceback for connection errors and automatic API key sanitization.

## Live Demo
**URL**: `https://rag-mini-project.vercel.app` (Replace with your actual URL)

---

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A GitHub account (for GitHub Models inference)
- Node.js & Vercel CLI (for deployment)

### 2. Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd rag_mini_project

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
You strictly use **GitHub Models** (Free Tier).
1. Get a token from [https://github.com/settings/tokens](https://github.com/settings/tokens).
2. Create a `.env` file locally:
   ```bash
   GITHUB_TOKEN=your_token_here_starting_with_github_pat
   ```
   *Note: The code automatically strips invisible whitespace from the token to prevent connection errors.*

### 4. Running Locally
```bash
# Use unvicorn to run the internal API
python -m uvicorn api.index:app --reload
```
Visit `http://127.0.0.1:8000` to see the backend, or open `public/index.html` in a browser.

---

## Deployment via Vercel

The project is configured for Vercel out of the box (`vercel.json`).

### 1. Install & Login
```bash
npm i -g vercel
vercel login
```

### 2. Deploy
```bash
vercel --prod
```

### 3. Configure Secrets (CRITICAL)
In your Vercel Project Dashboard:
1. Go to **Settings** > **Environment Variables**.
2. Add `GITHUB_TOKEN`.
   - **Value**: Your raw GitHub PAT.
   - **IMPORTANT**: Ensure you do NOT accidentally copy a newline at the end. (Though the code now handles this, it's best practice).

---

## Usage Guide

1. **Start the Chat**: Open the app.
2. **Check Health**: If it fails, check `/api/health` to see if the token is loaded (`token_set: true`).
3. **Upload Documents**: Click the 📎 Paperclip icon.
   - Upload `refund_policy.txt` or `shipping_policy.pdf`.
   - Wait for the "Indexed X/X chunks" message.
   - **Note on Limits**: Vercel has a 10-second timeout. Process small files (<20 pages) for best results.
4. **Ask Questions**:
   - "What is the refund window?"
   - "Can I return a gift card?"

---

## Architecture

- **Backend**: `api/index.py` (FastAPI) handles HTTP requests.
- **Core Logic**: `src/rag_engine.py` manages the document store logic.
   - **Ingestion**: Reads text/PDFs, chunks them (600 chars), and calls OpenAI Embeddings (`text-embedding-3-small`).
   - **Storage**: Python Lists (Ephemeral). **Does not persist after server sleep**.
   - **Retrieval**: Cosine similarity search using `NumPy`.
- **Frontend**: Vanilla JS/HTML (`public/folder`).

## Troubleshooting

- **"Connection Error" / "Illegal header value"**:
  - This typically means your `GITHUB_TOKEN` had a trailing newline/space. The latest code fixes this automatically with `.strip()`, but check your env vars if it persists.
- **"Indexed 0/X chunks"**:
  - This means the Embedding API failed silently. Check the Chat UI for the full error traceback.
- **"504 Gateway Timeout"**:
  - You uploaded a file that was too large (taking >10s to process). Split the file or upload smaller chunks.

## Future Improvements
- **Persistence**: Add Redis or a real Vector DB (Pinecone) to keep knowledge alive between sessions.
- **Async Ingestion**: Move ingestion to a background queue to bypass the 10s timeout.
