"""Factory for Vertex AI models."""

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Content
import vertexai.preview.generative_models as generative_models
from vertexai.language_models import ChatModel


class VertexAiFactory:
    """Factory for Vertex AI models."""

    def __init__(self):
        vertexai.init()
        self.models = {}

    def get_model(self, model_name: str) -> GenerativeModel | ChatModel:
        """Get the generative model."""
        if model_name in self.models:
            return self.models[model_name]
        if "gemini" in model_name:
            model = self._create_gemini_model(model_name)
        else:
            model = self._create_chat_model(model_name)
        self.models[model_name] = model
        return model

    def _create_gemini_model(self, model_name: str) -> GenerativeModel:
        """Create a Gemini model."""
        return GenerativeModel(
            model_name=model_name,
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

    def _create_chat_model(self, model_name: str) -> ChatModel:
        """Create a chat model."""
        return ChatModel.from_pretrained(model_name)

    def get_chat(self, model_name: str, history: list[Content] = None) -> ChatSession:
        """Get a chat session.

        Parameters:
        ----------
        model_name: str
            The name of the AI model.
        history: list[ChatMessage]
            The chat history (previous questions and answers).
        """
        if "gemini" in model_name:
            model: GenerativeModel = self.get_model(model_name)
            return model.start_chat(history=history)
        else:
            model: ChatModel = self.get_model(model_name)
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.9,
                "top_p": 1,
            }
            return model.start_chat(message_history=history, **parameters)
