from enum import Enum

from pydantic import BaseModel

from regai.evidence_models import EvidenceChunk
from regai.llm import ask_llm
from regai.regulatory_models import RegulatoryRequirement


class EvidenceRelevance(str, Enum):
    RELEVANT = "relevant"
    NOT_RELEVANT = "not_relevant"


class EvidenceRelevanceAssessment(BaseModel):
    requirement_id: str
    chunk_id: str
    relevance: EvidenceRelevance
    explanation: str


class EvidenceRelevanceResponse(BaseModel):
    assessments: list[EvidenceRelevanceAssessment]


def assess_evidence_relevance(
    requirement: RegulatoryRequirement,
    candidates: list[EvidenceChunk],
) -> EvidenceRelevanceResponse:
    candidate_data = [
        {
            "chunk_id": candidate.chunk_id,
            "heading": candidate.section_heading,
            "text": candidate.text,
        }
        for candidate in candidates
    ]

    prompt = f"""
Determine whether each evidence candidate is relevant to the
regulatory requirement.

The requirement_id is exactly:
{requirement.requirement_id}

You MUST return this exact value as requirement_id for every
assessment. Do not use a chunk_id as the requirement_id.

A candidate is relevant if its observed content directly addresses
the subject of the requirement.

Do not determine legal compliance.
Do not infer facts that are not present in the evidence.
Do not treat semantic similarity alone as sufficient.

Regulatory requirement:
{requirement.original_text}

Evidence candidates:
{candidate_data}

Return one assessment for each candidate.
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "evidence_relevance_assessments",
            "schema": {
                "type": "object",
                "properties": {
                    "assessments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "requirement_id": {
                                    "type": "string"
                                },
                                "chunk_id": {
                                    "type": "string"
                                },
                                "relevance": {
                                    "type": "string",
                                    "enum": [
                                        "relevant",
                                        "not_relevant",
                                    ],
                                },
                                "explanation": {
                                    "type": "string"
                                },
                            },
                            "required": [
                                "requirement_id",
                                "chunk_id",
                                "relevance",
                                "explanation",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["assessments"],
                "additionalProperties": False,
            },
        },
    }

    response = ask_llm(
        prompt,
        response_format=response_format,
    )

    return EvidenceRelevanceResponse.model_validate_json(
        response
    )