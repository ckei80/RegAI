from regai.regulatory_models import (
    RegulatoryRequirement,
    RequirementAnalysis,
)
from regai.retrieval import SemanticRetriever


class FakeEmbeddingProvider:

    def __init__(self, embeddings: dict[str, list[float]]):
        self.embeddings = embeddings
        self.calls = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return self.embeddings[text]


def create_requirement(
    requirement_id: str,
    topic: str,
    interpretation: str,
) -> RegulatoryRequirement:

    return RegulatoryRequirement(
        requirement_id=requirement_id,
        source="TEST",
        section=None,
        effective_date=None,
        original_text="Test requirement",
        analysis=RequirementAnalysis(
            topic=topic,
            interpretation=interpretation,
        ),
    )


def test_semantic_retriever_ranks_most_similar_requirement_first():

    requirement_a = create_requirement(
        "REQ-A",
        "Purpose",
        "The company must explain why personal data is processed.",
    )

    requirement_b = create_requirement(
        "REQ-B",
        "Identity",
        "The company must identify the data controller.",
    )

    query = "why the company uses customer data"

    embedding_provider = FakeEmbeddingProvider(
        {
            query: [1.0, 0.0],
            (
                "Purpose. "
                "The company must explain why personal data is processed."
            ): [1.0, 0.0],
            (
                "Identity. "
                "The company must identify the data controller."
            ): [0.0, 1.0],
        }
    )

    retriever = SemanticRetriever(
        embedding_provider,
        [
            requirement_b,
            requirement_a,
        ],
    )

    assert embedding_provider.calls == [
        (
            "Identity. "
            "The company must identify the data controller."
        ),
        (
            "Purpose. "
            "The company must explain why personal data is processed."
        ),
    ]

    results = retriever.search(
        query=query,
    )

    assert embedding_provider.calls == [
        (
            "Identity. "
            "The company must identify the data controller."
        ),
        (
            "Purpose. "
            "The company must explain why personal data is processed."
        ),
        query,
    ]

    assert results[0][0].requirement_id == "REQ-A"
    assert results[1][0].requirement_id == "REQ-B"