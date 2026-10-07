import time

from google import genai
from google.genai import errors


MODEL_ID = "gemini-3.1-flash-lite"


class LLMClient:
    def __init__(self) -> None:
        self.client = genai.Client()

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )

        if response.text is None:
            raise RuntimeError("Gemini returned no text response.")

        return response.text