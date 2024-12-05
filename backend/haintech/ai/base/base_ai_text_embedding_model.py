from abc import ABC, abstractmethod
from typing import List


class BaseAITextEmbeddingModel(ABC):
    """Base class for text embedding models."""

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Embeds text with a pre-trained model."""
        pass
