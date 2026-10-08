from regai.assessment import assess_regulatory_requirement
from regai.evidence_models import EvidenceChunk
from regai.evidence_retrieval import EvidenceRetriever
from regai.embeddings import LocalEmbeddingProvider
from regai.regulatory_models import RegulatoryRequirement
from regai.requirement_assessment import RequirementAssessment


def create_requirement() -> RegulatoryRequirement:
    return RegulatoryRequirement(
        requirement_id="ART13-B",
        source="GDPR",
        section="Article 13",
        effective_date="2018-05-25",
        original_text=(
            "The purposes of the processing for which the personal data "
            "are intended."
        ),
        analysis={
            "topic": "Purpose of processing",
            "interpretation": (
                "Explain the purposes for which personal data is processed."
            ),
        },
    )


def create_evidence() -> list[EvidenceChunk]:
    return [
        EvidenceChunk(
            chunk_id="chunk-001",
            source_url="https://example.com/privacy",
            page_title="Privacy Policy",
            section_heading="Purpose of using personal data",
            text=(
                "We use your email address to send order confirmations."
            ),
            retrieval_date="2026-10-05",
        ),
        EvidenceChunk(
            chunk_id="chunk-002",
            source_url="https://example.com/privacy",
            page_title="Privacy Policy",
            section_heading="Data retention",
            text=(
                "We retain personal data only for as long as necessary "
                "for the purposes for which it was collected."
            ),
            retrieval_date="2026-10-05",
        ),
        EvidenceChunk(
            chunk_id="chunk-003",
            source_url="https://example.com/privacy",
            page_title="Privacy Policy",
            section_heading="Sharing personal data",
            text=(
                "We may share personal data with service providers "
                "who help us operate our business."
            ),
            retrieval_date="2026-10-05",
        ),
    ]


def test_real_assessment_pipeline():
    requirement = create_requirement()
    evidence = create_evidence()

    embedding_provider = LocalEmbeddingProvider()

    evidence_retriever = EvidenceRetriever(
        embedding_provider=embedding_provider,
        chunks=evidence,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=evidence_retriever,
        top_k=3,
    )

    assert result is not None
    assert result.requirement_id == "ART13-B"
    assert result.assessment == RequirementAssessment.SUPPORTED
    assert result.explanation
   