from pydantic import BaseModel


class RegulatoryRequirement(BaseModel):
    requirement_id: str
    source: str
    section: str | None
    effective_date: str | None
    original_text: str
    topic: str
    interpretation: str
    evidence_needed: list[str]