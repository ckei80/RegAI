from regai.regulatory_document import RegulatoryDocument
from regai.regulatory_models import (
    RegulatoryRequirement,
    RequirementAnalysis,
)


def test_regulatory_document():
    analysis = RequirementAnalysis(
        topic="Transparency and Communication with Data Subjects",
        interpretation=(
            "The organisation must provide information to data subjects "
            "in a concise, transparent, intelligible and accessible manner."
        ),
    )

    requirement = RegulatoryRequirement(
        requirement_id="GDPR-ART12-001",
        source="European Union General Data Protection Regulation (GDPR)",
        section="Article 12",
        effective_date="2018-05-25",
        original_text=(
            "The controller shall take appropriate measures to provide "
            "any information referred to in Articles 13 and 14..."
        ),
        analysis=analysis,
    )

    document = RegulatoryDocument(
        source="European Union",
        title="General Data Protection Regulation",
        publication_date="2016-04-27",
        effective_date="2018-05-25",
        requirements=[requirement],
    )

    print(document)
    print()
    print(document.requirements[0].original_text)
    print()
    print(document.requirements[0].analysis.interpretation)

    assert document.source == "European Union"
    assert document.title == "General Data Protection Regulation"
    assert len(document.requirements) == 1
    assert document.requirements[0].requirement_id == "GDPR-ART12-001"
    assert document.requirements[0].analysis.topic == (
        "Transparency and Communication with Data Subjects"
    )