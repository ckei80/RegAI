from regai.evidence_assessment import (
    EvidenceAssessment,
    assess_evidence,
)
from regai.evidence_models import EvidenceChunk
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


def test_llm_assesses_evidence_against_requirement():
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
            "chunk-supported",
            "Purpose of using personal data",
            "We use your email address to send order confirmations.",
        ),
        create_chunk(
            "chunk-insufficient",
            "Legal basis for processing",
            "We process personal data for legitimate business purposes.",
        ),
        create_chunk(
            "chunk-contradicted",
            "Information provided to users",
            "We collect your email address but do not tell users why we use it.",
        ),
        create_chunk(
            "chunk-missing",
            "Personal data collected",
            "We collect your name and email address.",
        ),
    ]

    result = assess_evidence(
        requirement=requirement,
        candidates=candidates,
    )

    assessments = {
        assessment.chunk_id: assessment
        for assessment in result.assessments
    }

    assert (
        assessments["chunk-supported"].assessment
        == EvidenceAssessment.SUPPORTED
    )

    assert (
        assessments["chunk-insufficient"].assessment
        == EvidenceAssessment.INSUFFICIENT
    )

    assert (
        assessments["chunk-contradicted"].assessment
        == EvidenceAssessment.CONTRADICTED
    )

    assert (
        assessments["chunk-missing"].assessment
        == EvidenceAssessment.INSUFFICIENT
    )

    for assessment in result.assessments:
        assert assessment.requirement_id == requirement.requirement_id