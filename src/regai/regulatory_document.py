from pydantic import BaseModel

from regai.regulatory_models import RegulatoryRequirement

class RegulatoryDocument(BaseModel):
    source: str
    title: str
    publication_date: str | None
    effective_date: str | None
    requirements: list[RegulatoryRequirement]