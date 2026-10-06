from enum import Enum

from pydantic import BaseModel


class EvidenceSourceType(str, Enum):
    WEB_PAGE = "web_page"


class EvidenceSource(BaseModel):
    source_type: EvidenceSourceType
    url: str
    content: str