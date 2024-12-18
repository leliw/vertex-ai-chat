from typing import List

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel


class VertexAITextEmbeddingModel(BaseAITextEmbeddingModel):
    """Text embedding model using Vertex AI's TextEmbeddingModel."""

    def __init__(
        self, model_name: str = "text-multilingual-embedding-002", dimensionality=256
    ):
        self.model_name = model_name
        self.dimensionality = dimensionality
        self.model = TextEmbeddingModel.from_pretrained(model_name)

    async def get_embedding(self, text: str) -> List[float]:
        """Embeds texts with a pre-trained, foundational model."""
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT")]
        kwargs = (
            dict(output_dimensionality=self.dimensionality)
            if self.dimensionality
            else {}
        )
        embeddings = await self.model.get_embeddings_async(inputs, **kwargs)
        return embeddings[0].values
