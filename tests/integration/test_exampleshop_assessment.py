from pathlib import Path

import pytest

from regai.assessment import assess_regulatory_requirement
from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks
from regai.evidence_retrieval import EvidenceRetriever
from regai.embeddings import LocalEmbeddingProvider
from regai.requirement_assessment import RequirementAssessment
from regai.regulatory_models import RegulatoryRequirement


EXAMPLESHOP_DIR = Path("data/sample/exampleshop")


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


def load_chunks(filename: str) -> list[EvidenceChunk]:
    html = (
        EXAMPLESHOP_DIR / filename
    ).read_text(encoding="utf-8")

    return create_evidence_chunks(
        html=html,
        url=f"https://exampleshop.test/{filename}",
        retrieval_date="2026-10-08",
    )


@pytest.mark.parametrize(
    ("filename", "expected_assessment"),
    [
        (
            "supported.html",
            RequirementAssessment.SUPPORTED,
        ),
        (
            "insufficient.html",
            RequirementAssessment.INSUFFICIENT,
        ),
        (
            "potential_gap.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
    ],
)
def test_exampleshop_assessment(
    filename: str,
    expected_assessment: RequirementAssessment,
):
    requirement = create_requirement()
    chunks = load_chunks(filename)

    embedding_provider = LocalEmbeddingProvider()

    evidence_retriever = EvidenceRetriever(
        embedding_provider=embedding_provider,
        chunks=chunks,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=evidence_retriever,
        top_k=5,
    )

    assert result is not None
    assert result.requirement_id == "ART13-B"
    assert result.assessment == expected_assessment
    assert result.explanation