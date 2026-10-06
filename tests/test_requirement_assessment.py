from regai.evidence_models import EvidenceChunk
from regai.regulatory_models import RegulatoryRequirement
from regai.requirement_assessment import (
    RequirementAssessment,
    assess_requirement,
)


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


def test_llm_assesses_requirement_from_multiple_evidence_items():
    requirement = create_requirement()

    evidence = [
        create_chunk(
            "chunk-001",
            "Order processing",
            "We use your email address to send order confirmations.",
        ),
        create_chunk(
            "chunk-002",
            "Delivery",
            "We use your delivery address to deliver your orders.",
        ),
    ]

    result = assess_requirement(
        requirement=requirement,
        evidence=evidence,
    )

    print()
    print("Assessment:", result.assessment)
    print("Explanation:", result.explanation)

    assert result.requirement_id == requirement.requirement_id
    assert result.assessment == RequirementAssessment.SUPPORTED


def test_llm_identifies_insufficient_requirement_evidence():
    requirement = create_requirement()

    evidence = [
        create_chunk(
            "chunk-001",
            "Business purposes",
            "We process personal data for legitimate business purposes.",
        ),
    ]

    result = assess_requirement(
        requirement=requirement,
        evidence=evidence,
    )

    print()
    print("Assessment:", result.assessment)
    print("Explanation:", result.explanation)

    assert result.requirement_id == requirement.requirement_id
    assert result.assessment == RequirementAssessment.INSUFFICIENT


def test_llm_identifies_potential_gap():
    requirement = create_requirement()

    evidence = [
        create_chunk(
            "chunk-001",
            "Information provided to users",
            "We collect your email address but do not tell users why we use it.",
        ),
    ]

    result = assess_requirement(
        requirement=requirement,
        evidence=evidence,
    )

    print()
    print("Assessment:", result.assessment)
    print("Explanation:", result.explanation)

    assert result.requirement_id == requirement.requirement_id
    assert result.assessment == RequirementAssessment.POTENTIAL_GAP