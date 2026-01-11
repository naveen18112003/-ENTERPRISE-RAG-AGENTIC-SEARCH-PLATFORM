"""
Vector Store & RAG Retrieval

GitHub Models / OpenAI embeddings + FAISS vector store + RAG retriever
"""

import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

# 🔥 FORCE ENV LOAD (THIS WAS THE MISSING PIECE)
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# =========================
# FAISS CHECK
# =========================
try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False


# =========================
# EMBEDDING GENERATOR
# =========================
class EmbeddingGenerator:
    """
    Embedding priority:
    1. GitHub Models
    2. OpenAI
    3. Mock fallback
    """

    def __init__(self, model: str = "text-embedding-3-large"):
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            from openai import OpenAI
        except Exception:
            OpenAI = None

        github_token = os.getenv("GITHUB_TOKEN")
        openai_key = os.getenv("OPENAI_API_KEY")

        logger.error(f"[ENV CHECK] GITHUB_TOKEN visible = {bool(github_token)}")

        # ✅ GitHub Models (PRIMARY)
        if github_token and OpenAI is not None:
            try:
                self.client = OpenAI(
                    api_key=github_token,
                    base_url="https://models.inference.ai.azure.com"
                )
                logger.info("Initialized GitHub Models embeddings client")
                return
            except Exception as e:
                logger.error(f"GitHub Models init failed: {e}")

        # 🔁 OpenAI fallback
        if openai_key and OpenAI is not None:
            try:
                self.client = OpenAI(api_key=openai_key)
                logger.info("Initialized OpenAI embeddings client")
                return
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")

        # ❌ Mock fallback
        self.client = None
        logger.warning("No embedding provider configured; using deterministic mock embeddings")

    def embed(self, text: str) -> np.ndarray:
        if self.client:
            try:
                resp = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return np.array(resp.data[0].embedding, dtype=np.float32)
            except Exception as e:
                logger.error(f"Embedding API error: {e}; falling back to mock")

        # Deterministic mock embedding
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        base = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
        base = (base / 255.0) * 2 - 1
        dim = 1536
        reps = int(np.ceil(dim / base.size))
        vec = np.tile(base, reps)[:dim]
        return vec.astype(np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return np.vstack([self.embed(t) for t in texts])


# =========================
# FAISS VECTOR STORE
# =========================
class FAISSVectorStore:
    def __init__(self, index_path: str = "./vectorstore/faiss_index", dimension: int = 1536):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.index = None
        self.metadata: Dict[int, Dict[str, Any]] = {}
        self._load_or_create()

    def _load_or_create(self):
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"

        if index_file.exists() and metadata_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded FAISS index with {len(self.metadata)} vectors")
                return
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")

        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}

    def add(self, embeddings: np.ndarray, metadata_list: List[Dict[str, Any]]):
        emb = np.array(embeddings, dtype=np.float32)
        start = len(self.metadata)
        self.index.add(emb)
        for i, meta in enumerate(metadata_list):
            self.metadata[start + i] = meta
        logger.info(f"Added {len(metadata_list)} vectors to FAISS")

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float, Dict[str, Any]]]:
        q = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(q, k)
        results = []

        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            meta = self.metadata.get(int(idx), {})
            results.append((int(idx), float(dist), meta))

        return results

    def save(self):
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"
        faiss.write_index(self.index, str(index_file))
        with open(metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info("Saved FAISS index to disk")


# =========================
# RAG RETRIEVER
# =========================
class RAGRetriever:
    def __init__(self, vector_store: FAISSVectorStore, embedding_generator: EmbeddingGenerator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator

    def retrieve(self, query: str, k: int = 5, allowed_roles: Optional[List[str]] = None):
        emb = self.embedding_generator.embed(query)
        raw = self.vector_store.search(emb, k=k * 2)

        results = []
        for idx, dist, meta in raw:
            if allowed_roles:
                doc_roles = meta.get("access_roles", [])
                if not any(r in doc_roles for r in allowed_roles + ["admin"]):
                    continue

            results.append({
                "content": meta.get("content", ""),
                "source": meta.get("source", "unknown"),
                "similarity_score": 1 / (1 + dist),
                "distance": dist,
            })

        return results[:k]


# =========================
# VECTOR STORE MANAGER
# =========================
class VectorStoreManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        if not HAS_FAISS:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu")

        self.vector_store = FAISSVectorStore()
        self.embedding_generator = EmbeddingGenerator()
        self.retriever = RAGRetriever(self.vector_store, self.embedding_generator)
        self._initialized = True

    def add_documents(self, documents: List[Any]):
        from app.services.ingestion import Document

        texts = [d.content if isinstance(d, Document) else d.get("content", "") for d in documents]
        embeddings = self.embedding_generator.embed_batch(texts)
        metadata = [d.to_dict() if isinstance(d, Document) else d for d in documents]

        self.vector_store.add(embeddings, metadata)
        self.vector_store.save()

    def retrieve(self, query: str, k: int = 5, allowed_roles=None):
        return self.retriever.retrieve(query, k, allowed_roles)
