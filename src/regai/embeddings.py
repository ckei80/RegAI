from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the supplied text."""
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return embedding.tolist()