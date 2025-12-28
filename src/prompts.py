from typing import List, Dict

class PromptManager:
    def __init__(self):
        pass

    def build_context_string(self, chunks: List[str], metadatas: List[Dict]) -> str:
        """
        Formats retrieved chunks into a context string with citations.
        """
        context_parts = []
        for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
            source_file = meta.get('source', 'Unknown')
            context_parts.append(f"--- DOCUMENT {i+1} SOURCE: {source_file} ---\n{chunk}\n")
        
        return "\n".join(context_parts)

    def get_prompt_v1(self, query: str, context: str) -> list:
        """
        Baseline Prompt (Naive).
        Simple instruction to use context.
        """
        system_msg = "You are a helpful assistant for Acme Corp."
        user_msg = f"""
        Answer the user's question based on the following context:
        
        {context}
        
        Question: {query}
        """
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

    def get_prompt_v2(self, query: str, context: str) -> list:
        """
        Improved Prompt (Structured).
        - Role definition (Policy Expert).
        - Constraints (Only use provided context).
        - Hallucination check (If answer not in context, state it).
        - Formatting instructions (Markdown, use bullet points).
        - Citations (Mention source documents).
        """
        system_msg = """
        You are an expert Policy Assistant for Acme Corp. Your goal is to provide accurate, clear answers based ONLY on the provided policy documents.
        
        Guidelines:
        1. STRICTLY base your answer on the provided context. Do NOT use outside knowledge.
        2. If the answer is not found in the documents, clearly state: "I cannot find the answer to this question in the provided policies."
        3. Structure your answer using Markdown (headings, bullet points) for readability.
        4. Cite the source document for your answer (e.g., [Source: refund_policy.txt]).
        5. Be polite but professional.
        """
        
        user_msg = f"""
        CONTEXT:
        {context}
        
        USER QUESTION:
        {query}
        
        Provide your response below:
        """
        
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
