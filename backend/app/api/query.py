from fastapi import APIRouter
from app.services.vector_store import VectorStoreManager
from app.services.rag_answer import generate_answer

router = APIRouter()

@router.post("/query")
def query_rag(payload: dict):
    query = payload.get("query", "")
    roles = payload.get("roles", [])

    vsm = VectorStoreManager()
    contexts = vsm.retrieve(query, k=5, allowed_roles=roles)

    if not contexts:
        return {
            "answer": "The requested information is not available in the authorized documents.",
            "sources": [],
            "confidence": 0.0
        }

    return generate_answer(query, contexts)
