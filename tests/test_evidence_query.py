from regai.evidence_query import create_evidence_retrieval_query
from regai.regulatory_models import RegulatoryRequirement


def test_create_evidence_retrieval_query():
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

    query = create_evidence_retrieval_query(requirement)

    assert query == (
        "Purpose of processing. "
        "Explain the purposes for which personal data is processed."
    )