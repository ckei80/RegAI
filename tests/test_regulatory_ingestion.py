from regai.regulatory_ingestion import load_text_file
from regai.regulatory_source import SourceType


def test_load_text_file():
    source = load_text_file(
        "data/sample/gdpr_sample.txt",
        source_id="GDPR-SAMPLE",
    )

    assert source.source_id == "GDPR-SAMPLE"
    assert source.source_type == SourceType.TEXT
    assert source.location.endswith("gdpr_sample.txt")
    assert len(source.content) > 0