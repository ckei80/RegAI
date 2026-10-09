from pathlib import Path

import pytest

from regai.assessment import assess_regulatory_requirement
from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks
from regai.evidence_retrieval import EvidenceRetriever
from regai.embeddings import LocalEmbeddingProvider
from regai.requirement_assessment import RequirementAssessment
from regai.regulatory_models import RegulatoryRequirement

@pytest.fixture(scope="session")
def embedding_provider():
    return LocalEmbeddingProvider()

EVALUATION_DIR = Path("data/sample/exampleshop/evaluation")


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
        EVALUATION_DIR / filename
    ).read_text(encoding="utf-8")

    return create_evidence_chunks(
        html=html,
        url=f"https://exampleshop.test/evaluation/{filename}",
        retrieval_date="2026-10-08",
    )


@pytest.mark.parametrize(
    "filename, expected_assessment",
    [
        pytest.param(
            "01_explicit_purpose.html",
            RequirementAssessment.SUPPORTED,
            marks=pytest.mark.smoke,
        ),
        pytest.param(
            "02_multiple_purposes.html",
            RequirementAssessment.SUPPORTED,
        ),
        pytest.param(
            "03_vague_business_purpose.html",
            RequirementAssessment.INSUFFICIENT,
            marks=pytest.mark.smoke,
        ),
        (
            "04_data_collection_only.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
        (
            "05_legal_basis_only.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
        (
            "06_retention_only.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
        pytest.param(
            "07_explicit_missing_purpose.html",
            RequirementAssessment.POTENTIAL_GAP,
            marks=pytest.mark.smoke,
        ),
        (
            "08_purpose_plus_unrelated.html",
            RequirementAssessment.SUPPORTED,
        ),
        (
            "09_implied_purpose.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
        (
            "10_unrelated_privacy_content.html",
            RequirementAssessment.POTENTIAL_GAP,
        ),
    ],
)

def test_exampleshop_evaluation(
    filename: str,
    expected_assessment: RequirementAssessment,
    embedding_provider: LocalEmbeddingProvider,
):
    requirement = create_requirement()
    chunks = load_chunks(filename)

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