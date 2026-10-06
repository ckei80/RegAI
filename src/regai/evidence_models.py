from pydantic import BaseModel

class EvidenceChunk(BaseModel):
    chunk_id: str
    source_url: str
    page_title: str | None
    section_heading: str | None
    text: str
    retrieval_date: str


class EvidenceSearchResult(BaseModel):
    chunk: EvidenceChunk
    similarity: float