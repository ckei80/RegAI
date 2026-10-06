from regai.embeddings import LocalEmbeddingProvider
from regai.regulatory_models import RegulatoryRequirement
from regai.retrieval import SemanticRetriever


def create_requirement(
    requirement_id: str,
    topic: str,
    interpretation: str,
) -> RegulatoryRequirement:
    return RegulatoryRequirement(
        requirement_id=requirement_id,
        source="GDPR",
        section="Article 13",
        effective_date="2018-05-25",
        original_text="",
        analysis={
            "topic": topic,
            "interpretation": interpretation,
        },
    )


def test_real_embedding_retrieval_finds_relevant_requirement():
    requirements = [
        create_requirement(
            "ART13-B",
            "Purpose of processing",
            "Explain the purposes for which personal data is processed.",
        ),
        create_requirement(
            "ART13-A",
            "Identity of controller",
            "Identify the controller responsible for processing personal data.",
        ),
    ]

    provider = LocalEmbeddingProvider()

    retriever = SemanticRetriever(
        embedding_provider=provider,
        requirements=requirements,
    )

    results = retriever.search(
        "why the company uses customer data",
        top_k=2,
    )

    for requirement, similarity in results:
        print(
            requirement.requirement_id,
            similarity,
            requirement.analysis.topic,
        )

    assert results[0][0].requirement_id == "ART13-B"