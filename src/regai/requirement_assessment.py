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

* **supported**: The observed evidence explicitly identifies or describes what the requirement asks for.
* **insufficient**: Relevant evidence contains a statement about the requirement, but that statement is too vague to determine what purpose is being described.
* **potential_gap**: The observed evidence identifies a concrete concern that the requirement may not be adequately addressed, including an unexplained data use, a purpose that is merely implied by functionality, or an explicit omission.

### Decision rules

1. Assess only the evidence provided. Do not infer facts, assume hidden behaviour, or determine legal compliance.
2. Do not require proof that the evidence is exhaustive. If the evidence explicitly describes a purpose relevant to the requirement, classify it as `supported`, even if it does not establish whether additional purposes exist.
3. Do not downgrade an explicitly stated purpose merely because the evidence does not establish whether other purposes exist. Assess the purposes actually described; do not assume undisclosed additional purposes exist.
4. Distinguish an explicitly stated processing purpose from a description of a feature or functionality:
   * An explicit statement such as "We use your email address to send order confirmations" supports the purpose requirement.
   * A functionality statement such as "Customers can view their previous orders in their account" does not explicitly state why personal data is processed. Do not infer the processing purpose from the functionality alone. If this is the available evidence, classify it as `potential_gap`.
5. Use `insufficient` when the evidence does state a purpose, but the description is too vague to determine what purpose is meant. For example, "We process personal data for legitimate business purposes" does not identify specific purposes. Under this assessment policy, classify this as `insufficient` unless the observed evidence identifies a more specific omission or concern.
6. Distinguish simple data collection from explicit evidence of an omission:
   * If the evidence only says that personal data is collected or processed,
     without explaining its purpose or explicitly identifying missing
     information, classify it as `insufficient`.
   * If the evidence explicitly states that users are not told the purpose,
     or otherwise directly identifies the missing required information,
     classify it as `potential_gap`.
   * If the evidence describes functionality without explicitly explaining
     the processing purpose, classify it as `potential_gap`, as specified
     in rule 4.
   Explain the specific observed evidence supporting the classification.
7. Do not treat missing retrieved evidence as proof of an omission. If no relevant evidence is available, do not invent a gap. Base the classification on the evidence actually provided to the assessment.
8. Explain the classification using specific observed evidence. Make clear what the evidence establishes and, where applicable, what concrete concern remains unresolved.

`Supported` means the available evidence addresses the requirement; it does not establish that the organisation is legally compliant.

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

def assess_document_for_omission(
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
    ```

    Assess whether the available document evidence supports a potential
    omission of the regulatory requirement.

    The requirement_id is exactly:
    {requirement.requirement_id}

    You MUST return this exact value as requirement_id.

    Classify the result as exactly one of:

    * supported: The available evidence explicitly identifies or describes
    what the requirement asks for.
    * insufficient: The available evidence does not establish whether the
    requirement is addressed, or describes a purpose too vaguely to
    determine what it means.
    * potential_gap: The available evidence provides a defensible basis for
    identifying a possible omission of the required information.

    Decision rules:

    1. Assess all supplied chunks collectively. They represent the available
    extracted evidence, not necessarily the entire website or every
    document belonging to the organisation.
    2. Look for an explicit processing purpose anywhere in the supplied
    evidence, including chunks that might not have been retrieved by
    semantic search.
    3. A specific, explicitly stated processing purpose supports the
    requirement, even if other chunks are unrelated.
    4. A vague statement such as "We process personal data for legitimate
    business purposes" is insufficient unless other supplied evidence
    identifies a more specific purpose.
    5. A description of data collection, a legal basis, a retention period,
    or website functionality does not by itself establish the processing
    purpose.
    6. Do not infer a processing purpose from functionality alone.
    7. Do not treat the absence of a purpose in one chunk as proof that the
    purpose is absent from the supplied document evidence.
    8. Use potential_gap when the available document evidence provides
    a defensible basis for identifying a possible omission of the
    required processing purposes. This includes evidence describing
    data collection, processing, or retention without identifying
    the actual purposes anywhere in the supplied evidence, provided
    the evidence is sufficiently complete to support that conclusion.
    For example, "We retain personal data for the purposes for which
    it was collected" does not identify those purposes. Do not use
    insufficient merely because the purpose is not explicitly
    identified in an individual statement if the supplied evidence
    as a whole supports a possible omission.
    9. If the supplied evidence is too incomplete or ambiguous to support
    either supported or potential_gap, use insufficient.
    10. Do not determine legal compliance or invent facts.
    11. Explain the outcome using the observed evidence. Do not claim that
        the entire website or organisation was examined.

    Regulatory requirement:
    {requirement.original_text}

    Available document evidence:
    {evidence_data}
    """

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "document_omission_assessment",
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