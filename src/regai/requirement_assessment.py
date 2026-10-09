from enum import Enum

from pydantic import BaseModel

from regai.evidence_models import EvidenceChunk
from regai.llm import ask_llm
from regai.regulatory_models import RegulatoryRequirement


class RequirementAssessment(str, Enum):
    SUPPORTED = "supported"
    INSUFFICIENT = "insufficient"
    POTENTIAL_GAP = "potential_gap"


class RequirementAssessmentResult(BaseModel):
    requirement_id: str
    assessment: RequirementAssessment
    explanation: str


def assess_requirement(
    requirement: RegulatoryRequirement,
    evidence: list[EvidenceChunk],
) -> RequirementAssessmentResult:
    evidence_data = [
        {
            "chunk_id": chunk.chunk_id,
            "heading": chunk.section_heading,
            "text": chunk.text,
        }
        for chunk in evidence
    ]

    prompt = f"""
Assess the regulatory requirement using only the observed evidence
provided.

The requirement_id is exactly:
{requirement.requirement_id}

You MUST return this exact value as requirement_id.

Classify the requirement as exactly one of:

* supported: The observed evidence explicitly identifies or describes what the requirement asks for.
* insufficient: The evidence is relevant, but the information needed to address the requirement remains unclear or too vague.
* potential_gap: The evidence explicitly indicates that the requirement is not addressed or conflicts with it, including an explicit statement that required information is not provided or communicated.

Important rules:

* Do not determine legal compliance.
* Assess only what is supported by the observed evidence provided.
* Do not infer facts that are not present in the evidence.
* Do not speculate about hidden, undiscovered, or potentially unobserved behaviour.
* Do not require proof that the provided evidence is exhaustive.
* If the evidence explicitly identifies or describes what the requirement asks for, classify it as supported, even if the evidence does not establish that every possible aspect of the requirement has been addressed.
* Use insufficient when the observed evidence does not clearly establish what the requirement asks for, for example when the stated purpose is too vague to identify what personal data is used for.
* Use potential_gap only when the evidence explicitly indicates that the requirement is not addressed or conflicts with it.
* Absence of evidence is not, by itself, evidence of a potential gap.
* Supported means that the available evidence addresses the requirement; it does not mean that the organisation is legally compliant.
* If the evidence explicitly states that required information is not provided, disclosed, or communicated, classify it as potential_gap rather than insufficient. For example, if the requirement concerns explaining the purposes of processing personal data and the evidence states that users are not told why their data is used, classify it as potential_gap.


Regulatory requirement:
{requirement.original_text}

Observed evidence:
{evidence_data}
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "requirement_assessment",
            "schema": {
                "type": "object",
                "properties": {
                    "requirement_id": {
                        "type": "string"
                    },
                    "assessment": {
                        "type": "string",
                        "enum": [
                            "supported",
                            "insufficient",
                            "potential_gap",
                        ],
                    },
                    "explanation": {
                        "type": "string"
                    },
                },
                "required": [
                    "requirement_id",
                    "assessment",
                    "explanation",
                ],
                "additionalProperties": False,
            },
        },
    }

    response = ask_llm(
        prompt,
        response_format=response_format,
    )

    return RequirementAssessmentResult.model_validate_json(
        response
    )