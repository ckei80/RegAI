from pydantic import BaseModel


class RequirementAnalysis(BaseModel):
    topic: str
    interpretation: str


class RegulatoryRequirement(BaseModel):
    requirement_id: str
    source: str
    section: str | None
    effective_date: str | None
    original_text: str
    analysis: RequirementAnalysis