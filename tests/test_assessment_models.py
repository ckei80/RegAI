from regai.assessment_models import (
    AssessmentStatus,
    RequirementAssessment,
    RequirementEvidence,
)


def test_requirement_assessment():
    evidence = RequirementEvidence(
        url="https://example.com/privacy",
        observed_text="ExampleShop Ltd is the data controller.",
        retrieval_date="2026-09-30",
    )

    assessment = RequirementAssessment(
        requirement_id="REQ-001",
        status=AssessmentStatus.GREEN,
        explanation="The privacy policy identifies the controller.",
        evidence=[evidence],
    )

    assert assessment.requirement_id == "REQ-001"
    assert assessment.status == AssessmentStatus.GREEN
    assert len(assessment.evidence) == 1