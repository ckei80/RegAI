from regai.regulatory_ingestion import load_text_file
from regai.regulatory_processing import process_regulatory_source


def test_process_regulatory_source():
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    document = process_regulatory_source(
        source=source,
        title="GDPR Sample",
        effective_date="2026-01-01",
    )

    assert document.source == "GDPR-SAMPLE"
    assert document.title == "GDPR Sample"
    assert document.effective_date == "2026-01-01"

    assert len(document.requirements) > 0

    sections = [
        requirement.section
        for requirement in document.requirements
    ]

    assert "13(a)" in sections
    assert "13(b)" in sections
    assert "13(c)" in sections

    requirement_ids = [
    requirement.requirement_id
    for requirement in document.requirements
    ]

    assert "GDPR-SAMPLE-ART13-A" in requirement_ids
    assert "GDPR-SAMPLE-ART13-B" in requirement_ids
    assert "GDPR-SAMPLE-ART13-C" in requirement_ids