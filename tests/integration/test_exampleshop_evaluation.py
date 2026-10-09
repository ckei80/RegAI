import json
from pathlib import Path

import pytest

from regai.assessment import assess_regulatory_requirement
from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks
from regai.evidence_retrieval import EvidenceRetriever
from regai.embeddings import LocalEmbeddingProvider
from regai.requirement_assessment import RequirementAssessment
from regai.regulatory_models import RegulatoryRequirement


EVALUATION_DIR = Path("data/sample/exampleshop/evaluation")
CASES_FILE = EVALUATION_DIR / "cases.json"


@pytest.fixture(scope="session")
def embedding_provider():
    return LocalEmbeddingProvider()


def load_cases() -> list[dict]:
    return json.loads(CASES_FILE.read_text(encoding="utf-8"))


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
    html = (EVALUATION_DIR / filename).read_text(encoding="utf-8")

    return create_evidence_chunks(
        html=html,
        url=f"https://exampleshop.test/evaluation/{filename}",
        retrieval_date="2026-10-08",
    )


CASES = load_cases()


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            marks=pytest.mark.smoke if case["smoke"] else (),
            id=case["filename"],
        )
        for case in CASES
    ],
)

def test_exampleshop_evaluation(
    case: dict,
    embedding_provider: LocalEmbeddingProvider,
):
    requirement = create_requirement()
    chunks = load_chunks(case["filename"])

    evidence_retriever = EvidenceRetriever(
        embedding_provider=embedding_provider,
        chunks=chunks,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=evidence_retriever,
        top_k=5,
    )

    expected_assessment = RequirementAssessment(case["expected_assessment"])

    assert result is not None
    assert result.requirement_id == requirement.requirement_id
    assert result.assessment == expected_assessment
    assert result.explanation
