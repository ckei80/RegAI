from enum import Enum

from pydantic import BaseModel

from regai.evidence_models import EvidenceChunk
from regai.llm import ask_llm
from regai.regulatory_models import RegulatoryRequirement


class EvidenceAssessment(str, Enum):
    SUPPORTED = "supported"
    INSUFFICIENT = "insufficient"
    CONTRADICTED = "contradicted"


class RequirementEvidenceAssessment(BaseModel):
    requirement_id: str
    chunk_id: str
    assessment: EvidenceAssessment
    explanation: str


class EvidenceAssessmentResponse(BaseModel):
    assessments: list[RequirementEvidenceAssessment]


def assess_evidence(
    requirement: RegulatoryRequirement,
    candidates: list[EvidenceChunk],
) -> EvidenceAssessmentResponse:
    candidate_data = [
        {
            "chunk_id": candidate.chunk_id,
            "heading": candidate.section_heading,
            "text": candidate.text,
        }
        for candidate in candidates
    ]

    prompt = f"""
Assess each evidence candidate against the regulatory requirement.

The requirement_id is exactly:
{requirement.requirement_id}

You MUST return this exact value as requirement_id for every
assessment. Do not use a chunk_id as the requirement_id.

Classify each evidence candidate as exactly one of:

- supported: The evidence provides information that supports the
  regulatory requirement.
- insufficient: The evidence is relevant to the requirement but
  does not provide enough information to determine whether the
  requirement is satisfied.
- contradicted: The evidence explicitly indicates something that
  conflicts with the regulatory requirement.

Important rules:

- Do not determine legal compliance.
- Do not infer facts that are not present in the evidence.
- Absence of evidence is NOT contradiction.
- Do not treat semantic similarity alone as support.
- Base the assessment only on the observed evidence provided.

Regulatory requirement:
{requirement.original_text}

Evidence candidates:
{candidate_data}

Return one assessment for each candidate.
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "evidence_assessments",
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
                                "assessment": {
                                    "type": "string",
                                    "enum": [
                                        "supported",
                                        "insufficient",
                                        "contradicted",
                                    ],
                                },
                                "explanation": {
                                    "type": "string"
                                },
                            },
                            "required": [
                                "requirement_id",
                                "chunk_id",
                                "assessment",
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

    return EvidenceAssessmentResponse.model_validate_json(
        response
    )