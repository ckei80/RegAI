from regai.embeddings import LocalEmbeddingProvider
from regai.evidence_models import EvidenceChunk
from regai.evidence_query import create_evidence_retrieval_query
from regai.evidence_retrieval import EvidenceRetriever
from regai.regulatory_models import RegulatoryRequirement


def create_chunk(
    chunk_id: str,
    heading: str,
    text: str,
) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        source_url="https://example.com/privacy",
        page_title="Privacy Policy",
        section_heading=heading,
        text=text,
        retrieval_date="2026-10-05",
    )


def create_requirement(
    requirement_id: str,
    original_text: str,
    topic: str,
    interpretation: str,
) -> RegulatoryRequirement:
    return RegulatoryRequirement(
        requirement_id=requirement_id,
        source="GDPR",
        section="Article 13",
        effective_date="2018-05-25",
        original_text=original_text,
        analysis={
            "topic": topic,
            "interpretation": interpretation,
        },
    )


def test_real_embedding_retrieval_finds_relevant_evidence():
    chunks = [
        create_chunk(
            "chunk-001",
            "Purpose of using personal data",
            "We use your email address to send order confirmations.",
        ),
        create_chunk(
            "chunk-002",
            "Personal data collected",
            "We collect your name and delivery address.",
        ),
        create_chunk(
            "chunk-003",
            "Cookies",
            "We use cookies to understand how visitors use our website.",
        ),
        create_chunk(
            "chunk-004",
            "Contact us",
            "Contact us at support@example.com.",
        ),
        create_chunk(
            "chunk-005",
            "Legal basis for processing",
            "We process personal data where we have a lawful basis to do so.",
        ),
        create_chunk(
            "chunk-006",
            "Data retention",
            "We retain personal data only for as long as necessary for the purposes for which it was collected.",
        ),
        create_chunk(
            "chunk-007",
            "Sharing personal data",
            "We may share personal data with service providers who help us operate our business.",
        ),
        create_chunk(
            "chunk-008",
            "Your rights",
            "You have the right to request access to and correction or deletion of your personal data.",
        ),
        create_chunk(
            "chunk-009",
            "Controller identity",
            "The controller responsible for your personal data is ExampleShop Ltd. "
            "You can contact us at privacy@example.com.",
        ),
        create_chunk(
            "chunk-010",
            "Recipients of personal data",
            "We may share your personal data with payment providers, delivery "
            "companies, and other service providers.",
        ),
    ]

    requirements = [
        create_requirement(
            "ART13-A",
            (
                "the identity and the contact details of the controller and, "
                "where applicable, of the controller's representative"
            ),
            "Identity of controller",
            "Identify the controller responsible for processing personal data.",
        ),
        create_requirement(
            "ART13-B",
            (
                "the purposes of the processing for which the personal data "
                "are intended"
            ),
            "Purpose of processing",
            "Explain the purposes for which personal data is processed.",
        ),
        create_requirement(
            "ART13-C",
            (
                "the recipients or categories of recipients of the personal "
                "data, if any"
            ),
            "Recipients of personal data",
            "Identify the recipients or categories of recipients of personal data.",
        ),
    ]

    provider = LocalEmbeddingProvider()

    retriever = EvidenceRetriever(
        embedding_provider=provider,
        chunks=chunks,
    )

    for requirement in requirements:
        retrieval_query = create_evidence_retrieval_query(
            requirement
        )

        results = retriever.search(
            retrieval_query,
            top_k=5,
        )

        print()
        print(requirement.requirement_id)
        print("Query:", retrieval_query)

        for result in results:
            print(
                result.chunk.chunk_id,
                result.similarity,
                result.chunk.section_heading,
            )

    assert True