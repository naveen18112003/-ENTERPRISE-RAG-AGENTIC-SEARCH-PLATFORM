import sys
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_engine import RagEngine
from src.chunker import Chunker
from src.ingest import extract_text
from backend.app.services.agentic_search import agentic_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RagEngine()

class SearchRequest(BaseModel):
    query: str
    mode: str = "rag"

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Enterprise RAG + Agentic Search Platform API",
        "doc_count": rag.count()
    }

@app.post("/search")
async def search(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        if request.mode == "agentic":
            return agentic_search(request.query, rag)
        else:
            result = rag.generate_answer(request.query)
            return {
                "mode": "rag",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "context": result.get("context", [])
            }
    except Exception as e:
        import traceback
        print(f"Search Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    temp_path = os.path.join("data", file.filename)
    os.makedirs("data", exist_ok=True)
    
    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        text = extract_text(temp_path)
        if not text:
            return {"message": f"Error: No text could be extracted from {file.filename}"}
        
        chunker = Chunker(chunk_size=600, chunk_overlap=100)
        chunks = chunker.split_text(text)
        
        metadatas = [{"source": file.filename} for _ in chunks]
        count, error = rag.add_documents(chunks, metadatas)
        
        if error:
             return {"message": f"Upload failed: {error}"}
             
        return {
            "message": f"Successfully processed {file.filename}. Added {count} chunks to knowledge base.",
            "filename": file.filename,
            "chunks": count
        }
    except Exception as e:
        print(f"Upload Error: {str(e)}")
        return {"message": f"Error uploading file: {str(e)}"}
    finally:
        pass
