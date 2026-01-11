import logging
from typing import List, Dict
from app.services.llm import get_llm_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an enterprise RAG assistant. Answer ONLY using the provided context. "
    "If the answer is not in context, say you don't know."
)

def generate_answer(query: str, contexts: List[Dict]) -> Dict:
    client = get_llm_client()

    context_text = "\n\n".join(
        f"[Source: {c.get('source','unknown')}] {c.get('content','')}"
        for c in contexts
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {query}\n\nContext:\n{context_text}"}
    ]

    resp = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages,
        temperature=0.2
    )

    answer = resp.choices[0].message.content.strip()
    confidence = round(
        sum(c.get("similarity_score", 0) for c in contexts) / max(len(contexts), 1),
        2
    )

    return {
        "answer": answer,
        "sources": [
            {"source": c.get("source"), "score": c.get("similarity_score")}
            for c in contexts
        ],
        "confidence": confidence
    }
