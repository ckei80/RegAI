from enum import Enum

from pydantic import BaseModel


class SourceType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    URL = "url"


class RegulatorySource(BaseModel):
    source_id: str
    source_type: SourceType
    location: str
    content: str