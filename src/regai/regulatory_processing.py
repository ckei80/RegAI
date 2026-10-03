from regai.regulatory_document import RegulatoryDocument
from regai.regulatory_extraction import extract_requirements
from regai.regulatory_source import RegulatorySource


def process_regulatory_source(
    source: RegulatorySource,
    title: str,
    effective_date: str | None = None,
) -> RegulatoryDocument:

    requirements = extract_requirements(
        source_text=source.content,
        source=source.source_id,
        effective_date=effective_date,
    )

    return RegulatoryDocument(
        source=source.source_id,
        title=title,
        publication_date=None,
        effective_date=effective_date,
        requirements=requirements,
    )