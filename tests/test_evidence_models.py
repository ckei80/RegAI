from regai.evidence_models import EvidenceChunk


def test_evidence_chunk_can_be_created():
    chunk = EvidenceChunk(
        chunk_id="privacy-001",
        source_url="https://example.com/privacy",
        page_title="Privacy Policy",
        section_heading="How we use your information",
        text="We use your email address to send order confirmations.",
        retrieval_date="2026-10-04",
    )

    assert chunk.chunk_id == "privacy-001"
    assert chunk.source_url == "https://example.com/privacy"
    assert chunk.page_title == "Privacy Policy"
    assert chunk.section_heading == "How we use your information"
    assert chunk.text == (
        "We use your email address to send order confirmations."
    )