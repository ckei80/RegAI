from regai.regulatory_models import (
    RegulatoryRequirement,
    RequirementAnalysis,
)


def test_regulatory_requirement():
    analysis = RequirementAnalysis(
        topic="transparency",
        interpretation=(
            "Individuals must be informed about the purposes "
            "for which their personal data is processed."
        ),
    )

    requirement = RegulatoryRequirement(
        requirement_id="GDPR-ART12-001",
        source="GDPR",
        section="Articles 12-14",
        effective_date=None,
        original_text=(
            "The controller shall take appropriate measures to provide "
            "information to data subjects."
        ),
        analysis=analysis,
    )

    print(requirement)
    print()
    print(requirement.analysis.topic)
    print(requirement.analysis.interpretation)

    assert requirement.requirement_id == "GDPR-ART12-001"
    assert requirement.source == "GDPR"
    assert requirement.analysis.topic == "transparency"