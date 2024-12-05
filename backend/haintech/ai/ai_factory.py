"""Factory for Vertex AI models."""

from typing import Any, List
from warnings import deprecated
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    ChatSession as VertexaiChatSession,
    Content,
)
import vertexai.preview.generative_models as generative_models
from vertexai.language_models import ChatModel
from functools import lru_cache

from haintech.ai.vertex_ai.vertex_ai_text_embedding_model import (
    VertexAITextEmbeddingModel,
)


class AiFactory:
    """Factory for AI models."""

    def __init__(self):
        vertexai.init()

    def get_model(
        self, model_name: str, context: str = None, config: dict[str, Any] = None
    ) -> GenerativeModel | ChatModel:
        """Get the generative model."""
        system_instruction = context
        if config:
            config = tuple(config.items())
        else:
            config = tuple({})
        if "gemini" in model_name:
            model = self._create_gemini_model(
                model_name,
                system_instruction=system_instruction,
                config=config,
            )
        else:
            model = self._create_chat_model(model_name)
        return model

    @lru_cache(maxsize=16)
    def _create_gemini_model(
        self,
        model_name: str,
        system_instruction: str = None,
        config: tuple[str, Any] = None,
    ) -> GenerativeModel:
        """Create a Gemini model.

        Config as tuple is reqired by cache!!!
        """
        config = dict(config) or {
            "max_output_tokens": 8192,
            "temperature": 0.9,
            "top_p": 0.95,
        }
        return GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=config,
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )

    @lru_cache(maxsize=16)
    def _create_chat_model(self, model_name: str) -> ChatModel:
        """Create a chat model."""
        return ChatModel.from_pretrained(model_name)

    def get_chat(
        self,
        model_name: str,
        history: list[Content] = None,
        context: str = None,
        config: tuple[str, Any] = None,
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
            model: GenerativeModel = self.get_model(
                model_name, context=context, config=config
            )
            return model.start_chat(history=history)
        else:
            model: ChatModel = self.get_model(model_name, context=context)
            parameters = config or {
                "max_output_tokens": 1024,
                "temperature": 0.9,
                "top_p": 1,
            }
            return model.start_chat(message_history=history, **parameters)

    @lru_cache(maxsize=16)
    def get_text_embedding_model(
        self, model_name: str = "text-multilingual-embedding-002"
    ):
        return VertexAITextEmbeddingModel(model_name)
    
    @deprecated(
        "Use get_text_embedding_model instead.",
        version="0.1.0",
        action="always",
    )
    def get_embeddings(
        self,
        text: str,
        model_name: str = "text-multilingual-embedding-002",
    ) -> List[float]:
        """Embeds texts with a pre-trained, foundational model."""
        model = self.get_text_embedding_model(model_name)
        return model.get_embedding(text)
