from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import glob # imported here for smart_ingest
from dotenv import load_dotenv

load_dotenv()

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ingest import extract_text # Import the helper
from src.rag_engine import RagEngine
from src.chunker import Chunker

app = FastAPI(title="RAG Policy Assistant API", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Global State (Ephemeral for Vercel)
# Setup Global State (Ephemeral for Vercel)
rag = None

def get_rag():
    global rag
    if rag is None:
        print("Booting RAG Engine (Lazy)...")
        rag = RagEngine(ephemeral=True)
    return rag

# Helper to ingest manually (since we can't write to disk easily, we read from disk and put in memory)
def smart_ingest():
    # We re-implement a lightweight ingest here that targets the ephemeral DB instance
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    extensions = ["*.txt", "*.pdf"]
    file_paths = []
    for ext in extensions:
        file_paths.extend(glob.glob(os.path.join(data_dir, ext)))

    chunker = Chunker(chunk_size=600, chunk_overlap=100)
    
    all_chunks = []
    all_metadatas = []
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        
        # Use the shared helper
        text = extract_text(file_path)
            
        chunks = chunker.split_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename})
            
    if all_chunks:
        count, err = get_rag().add_documents(all_chunks, all_metadatas)
        if err:
            print(f"Ingest warning: {err}")
        print(f"Ingested {count} chunks into memory.")

# Trigger ingest on startup
# Trigger ingest on startup
# try:
#     print("Starting smart ingest...")
#     smart_ingest()
#     print("Smart ingest completed.")
# except Exception as e:
#     print(f"CRITICAL WARNING: Smart ingest failed on startup: {e}")
#     # We do NOT raise here, so the app still boots.

# SKIP INGEST ON BOOT FOR VERCEL
# Vercel has a 10s default timeout for serverless functions.
# Embedding all files in 'data/' involves OpenAI network calls which takes >10s.
print("App started. Skipping auto-ingest to prevent usage limits/timeouts. Please upload documents manually.")


class QueryRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str
    mode: str = "rag"  # "rag" or "agentic"

@app.get("/")
def home():
    return {"message": "RAG Policy Assistant API is running. Use /query to ask questions."}

@app.get("/health")
def health():
    # Basic health check that doesn't trigger RAG init if not needed
    token_set = ("GITHUB_TOKEN" in os.environ and bool(os.environ["GITHUB_TOKEN"])) or \
                ("OPENAI_API_KEY" in os.environ and bool(os.environ["OPENAI_API_KEY"]))
    doc_count = 0
    if rag:
        doc_count = rag.count()
    
    return {
        "status": "ok", 
        "rag_initialized": rag is not None,
        "token_set": token_set,
        "documents_in_memory": doc_count
    }

from fastapi import UploadFile, File
import shutil

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create a temporary file
        # Vercel only allows writing to /tmp
        import tempfile
        
        # Create a temp directory or use default temp path
        # We need to preserve the extension for extract_text to work
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        try:
            # Trigger Ingestion for this file
            text = extract_text(tmp_path)
            if not text:
                 return {"message": f"Uploaded {file.filename}, but no text could be extracted.", "filename": file.filename}

            chunker = Chunker(chunk_size=600, chunk_overlap=100)
            chunks = chunker.split_text(text)
            
            metadatas = [{"source": file.filename} for _ in chunks]
            
            if chunks:
                added_count, error_msg = get_rag().add_documents(chunks, metadatas)
                return {
                    "message": f"Processed {file.filename}. Indexed {added_count}/{len(chunks)} chunks." + (f" Error: {error_msg}" if error_msg else ""), 
                    "filename": file.filename,
                    "chunks_total": len(chunks),
                    "chunks_indexed": added_count,
                    "error": error_msg
                }
            else:
                return {"message": "Uploaded file but it resulted in 0 chunks.", "filename": file.filename}
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"Upload error: {e}") # Log to Vercel logs
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_endpoint(request: QueryRequest):
    # Retrieve & Generate
    # The RagEngine handles the OpenAI call internally now
    result = get_rag().generate_answer(request.query)
    
    return result

@app.post("/search")
def search_endpoint(request: SearchRequest):
    """
    Search endpoint with support for both RAG and Agentic modes.
    
    Request body:
    {
        "query": "your question here",
        "mode": "rag" | "agentic"
    }
    """
    # Validate mode
    if request.mode not in ["rag", "agentic"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mode: {request.mode}. Must be 'rag' or 'agentic'"
        )
    
    # Import search controller
    # Ensure root directory is in path for backend imports
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    from backend.app.controllers.search_controller import handle_search
    
    # Route to appropriate handler
    result = handle_search(request.query, request.mode, get_rag())
    
    return result
