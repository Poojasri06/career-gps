import os
import typing

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

try:
    import openai
    OPENAI_AVAILABLE = True
    if OPENAI_KEY:
        openai.api_key = OPENAI_KEY
except Exception:
    openai = None
    OPENAI_AVAILABLE = False


class LLMClient:
    """Minimal LLM client wrapper. Uses OpenAI if `OPENAI_API_KEY` is present, otherwise falls back to templates."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.available = OPENAI_AVAILABLE

    def generate_text(self, prompt: str, max_tokens: int = 256) -> str:
        if self.available and openai:
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                return f"(LLM failure) {e}"
        # Fallback simple echo / template
        return f"(No LLM) Summary: {prompt[:400]}"

    def embed(self, texts: typing.List[str]) -> typing.List[typing.List[float]]:
        """Return embeddings for texts. Uses OpenAI embeddings if available; returns empty vectors otherwise."""
        if self.available and openai:
            try:
                model = "text-embedding-3-small"
                resp = openai.Embedding.create(input=texts, model=model)
                return [item.embedding for item in resp.data]
            except Exception:
                pass
        # Fallback: return zero vectors (not suitable for production)
        return [[0.0] * 1536 for _ in texts]
