"""Factory for Vertex AI models."""

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Content
import vertexai.preview.generative_models as generative_models


class VertexAiFactory:
    """Factory for Vertex AI models."""

    def __init__(self):
        vertexai.init()
        self.model = self.get_model()

    def get_model(self) -> GenerativeModel:
        """Get the generative model."""
        return GenerativeModel(
            model_name="gemini-1.5-pro-preview-0409",
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            },
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )

    def get_chat(self, history: list[Content] = None) -> ChatSession:
        """Get a chat session.

        Parameters:
        ----------
        history: list[ChatMessage]
            The chat history (previous questions and answers).
        """
        return self.model.start_chat(history=history)
