from regai.assessment import assess_regulatory_requirement
from regai.evidence_models import (
    EvidenceChunk,
    EvidenceSearchResult,
)
from regai.evidence_relevance import (
    EvidenceRelevance,
    EvidenceRelevanceAssessment,
    EvidenceRelevanceResponse,
)
from regai.requirement_assessment import (
    RequirementAssessment,
    RequirementAssessmentResult,
)
from regai.regulatory_models import RegulatoryRequirement


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


def create_chunk(
    chunk_id: str,
    text: str,
) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        source_url="https://example.com/privacy",
        page_title="Privacy Policy",
        section_heading="Purpose of processing",
        text=text,
        retrieval_date="2026-10-05",
    )


class FakeEvidenceRetriever:
    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[EvidenceSearchResult]:
        return [
            EvidenceSearchResult(
                chunk=create_chunk(
                    "chunk-001",
                    "We use your email address to send order confirmations.",
                ),
                similarity=0.8,
            ),
            EvidenceSearchResult(
                chunk=create_chunk(
                    "chunk-002",
                    "We retain personal data only as long as necessary.",
                ),
                similarity=0.7,
            ),
        ]


def test_assessment_pipeline_returns_requirement_assessment(monkeypatch):
    requirement = create_requirement()

    def fake_relevance(
        requirement,
        candidates,
    ):
        return EvidenceRelevanceResponse(
            assessments=[
                EvidenceRelevanceAssessment(
                    requirement_id=requirement.requirement_id,
                    chunk_id="chunk-001",
                    relevance=EvidenceRelevance.RELEVANT,
                    explanation="Contains a processing purpose.",
                ),
                EvidenceRelevanceAssessment(
                    requirement_id=requirement.requirement_id,
                    chunk_id="chunk-002",
                    relevance=EvidenceRelevance.NOT_RELEVANT,
                    explanation="Concerns retention, not processing purpose.",
                ),
            ]
        )

    def fake_assessment(
        requirement,
        evidence,
    ):
        assert [chunk.chunk_id for chunk in evidence] == [
            "chunk-001"
        ]

        return RequirementAssessmentResult(
            requirement_id=requirement.requirement_id,
            assessment=RequirementAssessment.SUPPORTED,
            explanation="The evidence states a specific processing purpose.",
        )

    monkeypatch.setattr(
        "regai.assessment.assess_evidence_relevance",
        fake_relevance,
    )

    monkeypatch.setattr(
        "regai.assessment.assess_requirement",
        fake_assessment,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=FakeEvidenceRetriever(),
    )

    assert result is not None
    assert result.requirement_id == "ART13-B"
    assert result.assessment == RequirementAssessment.SUPPORTED


def test_assessment_pipeline_returns_potential_gap_when_no_relevant_evidence(
    monkeypatch,
):
    requirement = create_requirement()

    def fake_relevance(
        requirement,
        candidates,
    ):
        return EvidenceRelevanceResponse(
            assessments=[
                EvidenceRelevanceAssessment(
                    requirement_id=requirement.requirement_id,
                    chunk_id="chunk-001",
                    relevance=EvidenceRelevance.NOT_RELEVANT,
                    explanation="Does not address the requirement.",
                ),
                EvidenceRelevanceAssessment(
                    requirement_id=requirement.requirement_id,
                    chunk_id="chunk-002",
                    relevance=EvidenceRelevance.NOT_RELEVANT,
                    explanation="Does not address the requirement.",
                ),
            ]
        )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "Requirement assessment should not run without relevant evidence."
        )

    monkeypatch.setattr(
        "regai.assessment.assess_evidence_relevance",
        fake_relevance,
    )

    monkeypatch.setattr(
        "regai.assessment.assess_requirement",
        fail_if_called,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=FakeEvidenceRetriever(),
    )

    assert result is not None
    assert result.requirement_id == requirement.requirement_id
    assert result.assessment == RequirementAssessment.POTENTIAL_GAP