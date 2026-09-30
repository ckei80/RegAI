import json

from regai.llm import ask_llm
from regai.regulatory_models import RegulatoryRequirement, RequirementAnalysis


def extract_requirements(
    source_text: str,
    source: str,
    effective_date: str | None = None,
) -> list[RegulatoryRequirement]:
    response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "regulatory_requirements",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section": {
                                "type": ["string", "null"]
                            },
                            "original_text": {
                                "type": "string"
                            },
                            "analysis": {
                                "type": "object",
                                "properties": {
                                    "topic": {
                                        "type": "string"
                                    },
                                    "interpretation": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "topic",
                                    "interpretation"
                                ],
                                "additionalProperties": False
                            }
                        },
                        "required": [
                            "section",
                            "original_text",
                            "analysis"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            "required": [
                "requirements"
            ],
            "additionalProperties": False
        }
    }
}

    prompt = f"""
You are extracting regulatory requirements from a regulatory document.

Identify each distinct regulatory requirement in the source text.

For each requirement, return:

- section
- original_text
- analysis.topic
- analysis.interpretation

Rules:
- Preserve the original regulatory wording in original_text.
- Do not invent regulatory requirements.
- Keep distinct obligations separate where reasonable.
- interpretation should explain the requirement in plain language.
- Return valid JSON only.
- Return exactly one JSON object with a "requirements" array.

Source text:

{source_text}
"""

    response = ask_llm(
    prompt,
    response_format=response_format,
)
    data = json.loads(response)

    requirements = []

    for index, item in enumerate(data["requirements"], start=1):
        original_text = item["original_text"]

        if original_text not in source_text:
            raise ValueError(
                f"LLM returned original_text that was not found in the source "
                f"document for requirement {index}."
            )

        analysis = RequirementAnalysis(**item["analysis"])

        requirement = RegulatoryRequirement(
            requirement_id=f"REQ-{index:03d}",
            source=source,
            section=item.get("section"),
            effective_date=effective_date,
            original_text=item["original_text"],
            analysis=analysis,
        )

        requirements.append(requirement)

    return requirements