from pathlib import Path

from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks


EXAMPLESHOP_DIR = Path("data/sample/exampleshop")


def load_html(filename: str) -> str:
    return (
        EXAMPLESHOP_DIR / filename
    ).read_text(encoding="utf-8")


def test_supported_page_creates_expected_evidence_chunks():
    html = load_html("supported.html")

    chunks = create_evidence_chunks(
        html=html,
        url="https://exampleshop.test/privacy",
        retrieval_date="2026-10-08",
    )

    assert chunks

    purpose_chunks = [
        chunk
        for chunk in chunks
        if chunk.section_heading == "Why we use your personal data"
    ]

    assert len(purpose_chunks) == 1

    purpose_chunk = purpose_chunks[0]

    assert (
        "We use your email address to send order confirmations"
        in purpose_chunk.text
    )


def test_insufficient_page_creates_expected_evidence_chunks():
    html = load_html("insufficient.html")

    chunks = create_evidence_chunks(
        html=html,
        url="https://exampleshop.test/privacy",
        retrieval_date="2026-10-08",
    )

    assert chunks

    purpose_chunks = [
        chunk
        for chunk in chunks
        if chunk.section_heading == "How we handle personal data"
    ]

    assert len(purpose_chunks) == 1

    assert (
        "legitimate business purposes"
        in purpose_chunks[0].text
    )


def test_potential_gap_page_creates_expected_evidence_chunks():
    html = load_html("potential_gap.html")

    chunks = create_evidence_chunks(
        html=html,
        url="https://exampleshop.test/privacy",
        retrieval_date="2026-10-08",
    )

    assert chunks

    purpose_chunks = [
        chunk
        for chunk in chunks
        if chunk.section_heading == "Use of personal data"
    ]

    assert len(purpose_chunks) == 1

    assert "we do not tell users" in purpose_chunks[0].text
    assert "why their personal data is used" in purpose_chunks[0].text