import json
from pathlib import Path

from regai.regulatory_document import RegulatoryDocument
from regai.regulatory_models import RegulatoryRequirement


class RegulatoryStore:

    def __init__(self, path: str):
        self.path = Path(path)

    def save_document(self, document: RegulatoryDocument) -> None:
        documents = self._load_documents()

        documents[document.source] = document.model_dump(mode="json")

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                documents,
                indent=2,
            ),
            encoding="utf-8",
        )

    def get_document(
        self,
        source: str,
    ) -> RegulatoryDocument | None:

        documents = self._load_documents()

        data = documents.get(source)

        if data is None:
            return None

        return RegulatoryDocument.model_validate(data)

    def _load_documents(self) -> dict:
        if not self.path.exists():
            return {}

        return json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

    def get_requirements(
        self,
        source: str | None = None,
        section: str | None = None,
    ) -> list[RegulatoryRequirement]:

        documents = self._load_documents()

        requirements = []

        for document_data in documents.values():
            if source is not None:
                if document_data["source"] != source:
                    continue

            for requirement_data in document_data["requirements"]:
                if section is not None:
                    if requirement_data["section"] != section:
                        continue

                requirements.append(
                    RegulatoryRequirement.model_validate(
                        requirement_data
                    )
                )

        return requirements
    
    def search_requirements(
        self,
        query: str,
        source: str | None = None,
    ) -> list[RegulatoryRequirement]:

        query_terms = query.lower().split()

        requirements = self.get_requirements(
            source=source,
        )

        matches = []

        for requirement in requirements:
            searchable_text = (
                f"{requirement.analysis.topic} "
                f"{requirement.analysis.interpretation}"
            ).lower()

            if all(
                term in searchable_text
                for term in query_terms
            ):
                matches.append(requirement)

        return matches