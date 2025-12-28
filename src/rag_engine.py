import os
import uuid
from typing import List, Dict
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import traceback

load_dotenv()

class RagEngine:
    def __init__(self, persist_path: str = "chroma_db", collection_name: str = "policy_docs", ephemeral: bool = False):
        """
        Initialize RAG Engine with a lightweight in-memory vector store.
        Replaced ChromaDB to fit within Vercel's 250MB limit.
        """
        self.documents = []  # List of text chunks
        self.metadatas = []  # List of metadata dicts
        self.ids = []        # List of IDs
        self.embeddings = [] # List of embedding vectors (numpy arrays)

        # Initialize OpenAI client for GitHub Models
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            print("WARNING: GITHUB_TOKEN not found. RAG functionality will fail.")
        else:
            api_key = api_key.strip() # Remove trailing newlines that cause httpx ProtocolError
        
        self.openai_client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=api_key
        )
        
        # We also need an embedding client (can reuse the same client or logic)
        # GitHub models endoint for embeddings: text-embedding-3-small
        self.embedding_model = "text-embedding-3-small"

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using GitHub Models.
        """
        try:
            # Batching is better, but for simplicity/safety with mixed endpoints we do simple call
            # Note: GitHub models API might output different format, standard OpenAI call usually works
            response = self.openai_client.embeddings.create(
                input=texts,
                model=self.embedding_model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise e # Re-raise to surface to API

    def add_documents(self, chunks: List[str], metadatas: List[Dict]):
        """
        Add chunks to the in-memory store.
        """
        if not chunks:
            return

        print(f"Generating embeddings for {len(chunks)} chunks...")
        try:
            new_embeddings = self._get_embeddings(chunks)
        except Exception as e:
            full_error = f"{str(e)} | Type: {type(e).__name__} | Trace: {traceback.format_exc()}"
            print(f"Embedding failed: {full_error}")
            return 0, full_error
        
        # Filter out failed embeddings
        count = 0
        for i, text in enumerate(chunks):
            if new_embeddings[i]:
                self.documents.append(text)
                self.metadatas.append(metadatas[i])
                self.ids.append(str(uuid.uuid4()))
                self.embeddings.append(new_embeddings[i])
                count += 1
                
        print(f"Added {count} documents to memory.")
        return count, None


    def query(self, query_text: str, n_results: int = 3) -> Dict:
        """
        Query the in-memory store using cosine similarity.
        """
        if not self.embeddings:
            return {'documents': [[]], 'metadatas': [[]]}

        # 1. Embed query
        query_embedding_res = self._get_embeddings([query_text])
        if not query_embedding_res or not query_embedding_res[0]:
             return {'documents': [[]], 'metadatas': [[]]}
        
        query_embedding = query_embedding_res[0]

        # 2. Calculate Cosine Similarity
        # Sim(A, B) = dot(A, B) / (norm(A) * norm(B))
        
        query_vec = np.array(query_embedding)
        doc_vecs = np.array(self.embeddings)
        
        # Norms
        query_norm = np.linalg.norm(query_vec)
        doc_norms = np.linalg.norm(doc_vecs, axis=1)
        
        # Dot product
        dot_products = np.dot(doc_vecs, query_vec)
        
        # Cosine similarity
        # Avoid division by zero
        similarities = dot_products / (doc_norms * query_norm + 1e-9)
        
        # 3. Sort and Retrieve
        # argsort gives indices of sorted elements (ascending), so we take last n
        # Ensure we don't ask for more results than we have
        k = min(n_results, len(self.documents))
        if k == 0:
             return {'documents': [[]], 'metadatas': [[]]}

        sorted_indices = np.argsort(similarities)[::-1][:k]
        
        top_docs = [self.documents[i] for i in sorted_indices]
        top_metas = [self.metadatas[i] for i in sorted_indices]
        
        return {
            'documents': [top_docs],
            'metadatas': [top_metas]
        }

    def generate_answer(self, query_text: str, n_results: int = 3) -> Dict:
        """
        Retrieve context and generate answer using GitHub Models.
        """
        # 1. Retrieve
        retrieval_results = self.query(query_text, n_results=n_results)
        
        documents = retrieval_results['documents'][0] if retrieval_results['documents'] else []
        metadatas = retrieval_results['metadatas'][0] if retrieval_results['metadatas'] else []
        
        if not documents:
            return {
                "answer": "I couldn't find any relevant information in the documents.",
                "context": [],
                "sources": []
            }
            
        # 2. Construct Prompt
        context_str = "\n\n".join([f"--- Source: {m.get('source', 'Unknown')} ---\n{d}" for d, m in zip(documents, metadatas)])
        
        system_prompt = "You are a helpful assistant for a policy RAG system. Answer the user's question based ONLY on the provided context. If the answer is not in the context, say you don't know."
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query_text}"
        
        # 3. Generate
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error generating answer: {e}"
            
        return {
            "answer": answer,
            "context": documents,
            "sources": [m.get('source', 'Unknown') for m in metadatas]
        }

    def count(self):
        return len(self.documents)
