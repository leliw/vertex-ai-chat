"""Factory for Vertex AI models."""

from typing import List, Optional
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    ChatSession as VertexaiChatSession,
    Content,
)
import vertexai.preview.generative_models as generative_models
from vertexai.language_models import ChatModel, TextEmbeddingInput, TextEmbeddingModel


class AIModelFactory:
    """Factory for AI models."""

    def __init__(self):
        vertexai.init()
        self.models = {}

    def get_model(
        self, model_name: str, context: str = None
    ) -> GenerativeModel | ChatModel:
        """Get the generative model."""
        if context and model_name in self.models:
            return self.models[model_name]
        system_instruction = context
        if "gemini" in model_name:
            model = self._create_gemini_model(
                model_name, system_instruction=system_instruction
            )
        else:
            model = self._create_chat_model(model_name)
        if not context:
            self.models[model_name] = model
        return model

    def _create_gemini_model(
        self, model_name: str, system_instruction: str = None
    ) -> GenerativeModel:
        """Create a Gemini model."""
        return GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
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

    def get_chat(
        self, model_name: str, history: list[Content] = None, context: str = None
    ) -> VertexaiChatSession:
        """Get a chat session.

        Parameters:
        ----------
        model_name: str
            The name of the AI model.
        history: list[ChatMessage]
            The chat history (previous questions and answers).
        context: str
            The context of the chat session.
        """
        if "gemini" in model_name:
            model: GenerativeModel = self.get_model(model_name, context=context)
            return model.start_chat(history=history)
        else:
            model: ChatModel = self.get_model(model_name, context=context)
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.9,
                "top_p": 1,
            }
            return model.start_chat(message_history=history, **parameters)

    def get_text_embedding_model(self, model_name: str = None):
        if not model_name:
            model_name = "text-multilingual-embedding-002"
        if model_name in self.models:
            return self.models[model_name]
        else:
            model = TextEmbeddingModel.from_pretrained(model_name)
            self.models[model_name] = model
            return model

    def embed_text(
        self,
        text: str,
        task: str = "RETRIEVAL_DOCUMENT",
        title: str = None,
        model_name: str = "text-multilingual-embedding-002",
        dimensionality: Optional[int] = 256,
    ) -> List[float]:
        """Embeds texts with a pre-trained, foundational model."""
        model = self.get_text_embedding_model(model_name)
        inputs = [TextEmbeddingInput(text, task, title=title)]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        embeddings = model.get_embeddings(inputs, **kwargs)
        return embeddings[0].values
