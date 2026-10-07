from regai.evidence_query import create_evidence_retrieval_query
from regai.evidence_relevance import (
    EvidenceRelevance,
    assess_evidence_relevance,
)
from regai.evidence_retrieval import EvidenceRetriever
from regai.requirement_assessment import (
    RequirementAssessmentResult,
    assess_requirement,
)
from regai.regulatory_models import RegulatoryRequirement


def assess_regulatory_requirement(
    requirement: RegulatoryRequirement,
    evidence_retriever: EvidenceRetriever,
    top_k: int = 5,
) -> RequirementAssessmentResult | None:
    retrieval_query = create_evidence_retrieval_query(
        requirement
    )

    search_results = evidence_retriever.search(
        retrieval_query,
        top_k=top_k,
    )

    candidates = [
        result.chunk
        for result in search_results
    ]

    if not candidates:
        return None

    relevance_result = assess_evidence_relevance(
        requirement=requirement,
        candidates=candidates,
    )

    relevant_chunk_ids = {
        assessment.chunk_id
        for assessment in relevance_result.assessments
        if assessment.relevance == EvidenceRelevance.RELEVANT
    }

    relevant_evidence = [
        candidate
        for candidate in candidates
        if candidate.chunk_id in relevant_chunk_ids
    ]

    if not relevant_evidence:
        return None

    return assess_requirement(
        requirement=requirement,
        evidence=relevant_evidence,
    )