from regai.regulatory_ingestion import load_text_file
from regai.regulatory_processing import process_regulatory_source
from regai.regulatory_store import RegulatoryStore
from regai.regulatory_models import RegulatoryRequirement


def test_save_and_load_regulatory_document(tmp_path):
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    document = process_regulatory_source(
        source=source,
        title="GDPR Sample",
        effective_date="2026-01-01",
    )

    store = RegulatoryStore(
        str(tmp_path / "regulatory_knowledge.json")
    )

    store.save_document(document)

    loaded_document = store.get_document(
        "GDPR-SAMPLE"
    )

    assert loaded_document is not None

    assert loaded_document.source == "GDPR-SAMPLE"
    assert loaded_document.title == "GDPR Sample"
    assert loaded_document.effective_date == "2026-01-01"

    assert len(loaded_document.requirements) == 3

    requirement_ids = [
        requirement.requirement_id
        for requirement in loaded_document.requirements
    ]

    assert "GDPR-SAMPLE-ART13-A" in requirement_ids
    assert "GDPR-SAMPLE-ART13-B" in requirement_ids
    assert "GDPR-SAMPLE-ART13-C" in requirement_ids

def test_get_requirements_by_section(tmp_path):
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    document = process_regulatory_source(
        source=source,
        title="GDPR Sample",
        effective_date="2026-01-01",
    )

    store = RegulatoryStore(
        str(tmp_path / "regulatory_knowledge.json")
    )

    store.save_document(document)

    requirements = store.get_requirements(
        source="GDPR-SAMPLE",
        section="13(b)",
    )

    assert len(requirements) == 1
    assert (
        requirements[0].requirement_id
        == "GDPR-SAMPLE-ART13-B"
    )
    assert isinstance(
        requirements[0],
        RegulatoryRequirement,
    )

def test_search_requirements_by_keywords(tmp_path):
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    document = process_regulatory_source(
        source=source,
        title="GDPR Sample",
        effective_date="2026-01-01",
    )

    store = RegulatoryStore(
        str(tmp_path / "regulatory_knowledge.json")
    )

    store.save_document(document)

    requirements = store.search_requirements(
        "purpose processing",
    )

    assert len(requirements) == 1

    assert (
        requirements[0].requirement_id
        == "GDPR-SAMPLE-ART13-B"
    )

def test_search_requires_matching_words(tmp_path):
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    document = process_regulatory_source(
        source=source,
        title="GDPR Sample",
        effective_date="2026-01-01",
    )

    store = RegulatoryStore(
        str(tmp_path / "regulatory_knowledge.json")
    )

    store.save_document(document)

    requirements = store.search_requirements(
        "why the company uses customer data",
    )

    assert requirements == []