"""
LLM Integration & Answer Generation

WHAT: Uses GitHub Models / OpenAI for answer generation
WHY: LLM is only used for reasoning, never for storage
HOW: Combines RAG context + query, generates grounded answers
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM Client with provider priority:
    1. GitHub Models (recommended)
    2. OpenAI
    3. Mock fallback
    """

    def __init__(self, model: str = "openai/gpt-4o"):
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

        logger.info(f"[LLM ENV CHECK] GitHub token present = {bool(github_token)}")

        if github_token and OpenAI is not None:
            try:
                self.client = OpenAI(
                    api_key=github_token,
                    base_url="https://models.inference.ai.azure.com"
                )
                logger.info("Initialized GitHub Models LLM client")
                return
            except Exception as e:
                logger.error(f"GitHub Models init failed: {e}")

        if openai_key and OpenAI is not None:
            try:
                self.client = OpenAI(api_key=openai_key)
                logger.info("Initialized OpenAI LLM client")
                return
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")

        self.client = None
        logger.warning("No LLM provider configured; using mock LLM")

    def generate_answer(
        self,
        query: str,
        context: str,
        strategy: str = "vector_search",
    ) -> str:
        """
        Generate answer using RAG context

        RULES:
        - Answer ONLY from provided context
        - No hallucination
        - Explicitly say if answer not found
        """

        system_prompt = (
            "You are an enterprise RAG assistant.\n"
            "Rules:\n"
            "1. Answer ONLY using the provided context\n"
            "2. Do NOT add external knowledge\n"
            "3. If answer is missing, say you don't know\n"
            "4. Be concise and professional\n"
        )

        user_message = f"""
Question:
{query}

Retrieved Context:
{context}

Answer strictly based on the above context.
"""

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.2,
                    max_tokens=800,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"LLM error: {e}")
                return "Error generating answer from language model."

        if not context or not context.strip():
            return "The requested information is not available in the authorized documents."

        return (
            f"(Mock LLM)\n"
            f"The answer to '{query}' is based only on the provided context."
        )
