from regai.evidence_models import EvidenceChunk
from regai.evidence_relevance import (
    EvidenceRelevance,
    assess_evidence_relevance,
)
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


def test_llm_distinguishes_relevant_evidence():
    requirement = RegulatoryRequirement(
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

    candidates = [
        create_chunk(
            "chunk-005",
            "Legal basis for processing",
            "We process personal data where we have a lawful basis to do so.",
        ),
        create_chunk(
            "chunk-001",
            "Purpose of using personal data",
            "We use your email address to send order confirmations.",
        ),
    ]

    result = assess_evidence_relevance(
        requirement=requirement,
        candidates=candidates,
    )

    assessments = {
        assessment.chunk_id: assessment
        for assessment in result.assessments
    }

    assert (
        assessments["chunk-005"].requirement_id
        == requirement.requirement_id
    )

    assert (
        assessments["chunk-005"].relevance
        == EvidenceRelevance.NOT_RELEVANT
    )

    assert (
        assessments["chunk-001"].requirement_id
        == requirement.requirement_id
    )

    assert (
        assessments["chunk-001"].relevance
        == EvidenceRelevance.RELEVANT
    )