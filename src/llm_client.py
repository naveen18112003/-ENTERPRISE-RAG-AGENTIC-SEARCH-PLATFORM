from openai import OpenAI
import os

class LLMClient:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        # Prioritize GITHUB_TOKEN for GitHub Models, otherwise allow OPENAI_API_KEY
        self.api_key = api_key or os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")
        
        # GitHub Models endpoint usually requires a specific base_url
        # If GITHUB_TOKEN is set, we default to the GitHub AI inference endpoint if not provided
        default_base_url = "https://models.github.ai/inference" if os.getenv("GITHUB_TOKEN") else None
        self.base_url = base_url or os.getenv("LLM_BASE_URL") or default_base_url
        
        # Default model logic
        self.default_model = model or os.getenv("LLM_MODEL") or "openai/gpt-4o"

        if not self.api_key:
            raise ValueError("API Key is missing. Please set GITHUB_TOKEN (for GitHub Models) or OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate_response(self, messages: list, model: str = None, temperature: float = 0.0) -> str:
        # Use instance default if model not provided
        target_model = model or self.default_model
        
        # User documentation suggests 'openai/gpt-4o' is required for the GitHub endpoint,
        # so we do NOT strip 'openai/' prefix anymore.
        
        # Debugging info (temporary)
        print(f"[DEBUG] Using LLM Model: {target_model}")
        print(f"[DEBUG] Using Base URL: {self.base_url}")

        try:
            response = self.client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"
