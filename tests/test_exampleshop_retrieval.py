from pathlib import Path

from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks
from regai.evidence_retrieval import EvidenceRetriever
from regai.embeddings import LocalEmbeddingProvider


EXAMPLESHOP_DIR = Path("data/sample/exampleshop")


def load_chunks(filename: str) -> list[EvidenceChunk]:
    html = (
        EXAMPLESHOP_DIR / filename
    ).read_text(encoding="utf-8")

    return create_evidence_chunks(
        html=html,
        url=f"https://exampleshop.test/{filename}",
        retrieval_date="2026-10-08",
    )


def test_supported_page_retrieves_purpose_evidence_first():
    chunks = load_chunks("supported.html")

    provider = LocalEmbeddingProvider()

    retriever = EvidenceRetriever(
        embedding_provider=provider,
        chunks=chunks,
    )

    results = retriever.search(
        "The purposes for which personal data is processed.",
        top_k=3,
    )

    assert results

    top_result = results[0]

    assert (
        top_result.chunk.section_heading
        == "Why we use your personal data"
    )

    assert (
        "send order confirmations"
        in top_result.chunk.text
    )