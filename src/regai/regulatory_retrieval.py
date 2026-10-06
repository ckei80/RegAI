from regai.regulatory_models import (
    RegulatoryRequirement,
    RequirementRetrievalRepresentation,
)


def create_retrieval_representation(
    requirement: RegulatoryRequirement,
) -> RequirementRetrievalRepresentation:
    return RequirementRetrievalRepresentation(
        text=(
            f"{requirement.analysis.topic}. "
            f"{requirement.analysis.interpretation}"
        )
    )