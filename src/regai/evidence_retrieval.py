from regai.evidence_models import (
    EvidenceChunk,
    EvidenceSearchResult,
)
from regai.embeddings import EmbeddingProvider
from regai.retrieval import cosine_similarity


class EvidenceRetriever:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        chunks: list[EvidenceChunk],
    ):
        self.embedding_provider = embedding_provider
        self.chunks = chunks
        self.embeddings = {
            chunk.chunk_id: (
                self.embedding_provider.embed(
                    (
                        f"{chunk.section_heading}. {chunk.text}"
                        if chunk.section_heading
                        else chunk.text
                    )
                )
            )
            for chunk in chunks
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[EvidenceSearchResult]:
        query_embedding = self.embedding_provider.embed(query)

        results = []

        for chunk in self.chunks:
            chunk_embedding = self.embeddings[chunk.chunk_id]

            similarity = cosine_similarity(
                query_embedding,
                chunk_embedding,
            )

            results.append(
                EvidenceSearchResult(
                    chunk=chunk,
                    similarity=similarity,
                )
            )

        results.sort(
            key=lambda result: result.similarity,
            reverse=True,
        )

        return results[:top_k]