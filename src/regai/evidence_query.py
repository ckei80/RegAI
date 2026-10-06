from regai.regulatory_models import RegulatoryRequirement


def create_evidence_retrieval_query(
    requirement: RegulatoryRequirement,
) -> str:
    return (
        f"{requirement.analysis.topic}. "
        f"{requirement.analysis.interpretation}"
    )