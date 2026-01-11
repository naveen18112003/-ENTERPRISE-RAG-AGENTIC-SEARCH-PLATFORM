"""
Search Controller

Routes search requests to either RAG or Agentic Search based on mode.
"""

from typing import Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.rag_engine import RagEngine
from backend.app.services.agentic_search import agentic_search


def handle_search(query: str, mode: str, rag_engine: RagEngine) -> Dict:
    """
    Handle search request and route to appropriate handler.
    
    Args:
        query: User query string
        mode: "rag" or "agentic"
        rag_engine: Initialized RagEngine instance
        
    Returns:
        Dictionary with search results
    """
    if mode == "agentic":
        return agentic_search(query, rag_engine)
    else:
        # Default to simple RAG
        result = rag_engine.generate_answer(query)
        return {
            "mode": "rag",
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "context": result.get("context", [])
        }

