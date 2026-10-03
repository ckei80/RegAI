import json

from regai.llm import ask_llm
from regai.regulatory_models import RegulatoryRequirement, RequirementAnalysis
from regai.regulatory_segmentation import segment_regulatory_text


def extract_requirements(
    source_text: str,
    source: str,
    effective_date: str | None = None,
) -> list[RegulatoryRequirement]:

    segments = segment_regulatory_text(source_text)

    segments_by_id = {
        segment.segment_id: segment
        for segment in segments
    }

    segment_text = "\n\n".join(
        f"Segment ID: {segment.segment_id}\n"
        f"Section: {segment.section}\n"
        f"Source text:\n{segment.original_text}"
        for segment in segments
    )

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
                                "source_segment_id": {
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
                                        "interpretation",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                            "required": [
                                "source_segment_id",
                                "analysis",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["requirements"],
                "additionalProperties": False,
            },
        },
    }

    prompt = f"""
You are analysing regulatory requirements.

The application has already identified the exact source segments.

You must NOT reproduce or modify the regulatory source text.

For each independently assessable regulatory obligation:

- return the source_segment_id of the segment being analysed
- provide analysis.topic
- provide analysis.interpretation

Rules:
- Use only the supplied source segments.
- Do not invent source segment IDs.
- Do not reproduce the source text.
- Keep independently assessable obligations separate.
- interpretation should explain the requirement in plain language.

Source segments:

{segment_text}
"""

    response = ask_llm(
        prompt,
        response_format=response_format,
    )

    print("LLM response:", response)

    data = json.loads(response)

    requirements = []

    for index, item in enumerate(data["requirements"], start=1):
        segment_id = item["source_segment_id"]

        if segment_id not in segments_by_id:
            raise ValueError(
                f"LLM returned unknown source segment ID: {segment_id}"
            )

        segment = segments_by_id[segment_id]

        analysis = RequirementAnalysis(**item["analysis"])

        requirement = RegulatoryRequirement(
            requirement_id=f"{source}-{segment.segment_id}",
            source=source,
            section=segment.section,
            effective_date=effective_date,
            original_text=segment.original_text,
            analysis=analysis,
        )

        requirements.append(requirement)

    return requirements