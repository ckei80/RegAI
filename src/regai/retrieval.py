from regai.embeddings import EmbeddingProvider
from regai.regulatory_models import RegulatoryRequirement


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


class SemanticRetriever:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        requirements: list[RegulatoryRequirement],
    ):
        self.embedding_provider = embedding_provider
        self.requirements = requirements

        self.embeddings = {
            requirement.requirement_id: (
                self.embedding_provider.embed(
                    self._requirement_text(requirement)
                )
            )
            for requirement in requirements
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[tuple[RegulatoryRequirement, float]]:

        query_embedding = self.embedding_provider.embed(query)

        results = []

        for requirement in self.requirements:

            requirement_embedding = self.embeddings[
                requirement.requirement_id
            ]

            similarity = cosine_similarity(
                query_embedding,
                requirement_embedding,
            )

            results.append(
                (requirement, similarity)
            )

        results.sort(
            key=lambda result: result[1],
            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def _requirement_text(
        requirement: RegulatoryRequirement,
    ) -> str:

        return (
            f"{requirement.analysis.topic}. "
            f"{requirement.analysis.interpretation}"
        )