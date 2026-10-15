import json
from pathlib import Path

from pydantic import BaseModel

from regai.evidence_models import EvidenceChunk
from regai.evidence_source import EvidenceSourceType


class StoredEvidenceSource(BaseModel):
    source_type: EvidenceSourceType
    url: str
    retrieval_date: str
    chunks: list[EvidenceChunk]


class EvidenceStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save_source(
        self,
        source_type: EvidenceSourceType,
        url: str,
        retrieval_date: str,
        chunks: list[EvidenceChunk],
    ) -> None:
        sources = self._load_sources()

        source = StoredEvidenceSource(
            source_type=source_type,
            url=url,
            retrieval_date=retrieval_date,
            chunks=chunks,
        )

        sources[url] = source.model_dump(mode="json")

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(sources, indent=2),
            encoding="utf-8",
        )

    def get_source(
        self,
        url: str,
    ) -> StoredEvidenceSource | None:
        sources = self._load_sources()
        data = sources.get(url)

        if data is None:
            return None

        return StoredEvidenceSource.model_validate(data)

    def get_sources(self) -> list[StoredEvidenceSource]:
        sources = self._load_sources()

        return [
            StoredEvidenceSource.model_validate(data)
            for data in sources.values()
        ]

    def get_chunks(
        self,
        source_url: str | None = None,
    ) -> list[EvidenceChunk]:
        sources = self.get_sources()
        chunks = []

        for source in sources:
            if source_url is not None and source.url != source_url:
                continue

            chunks.extend(source.chunks)

        return chunks

    def _load_sources(self) -> dict:
        if not self.path.exists():
            return {}

        content = self.path.read_text(encoding="utf-8")

        if not content.strip():
            return {}

        return json.loads(content)