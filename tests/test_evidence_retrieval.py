from regai.evidence_models import EvidenceChunk
from regai.evidence_retrieval import EvidenceRetriever


class FakeEmbeddingProvider:
    def __init__(self, embeddings: dict[str, list[float]]):
        self.embeddings = embeddings
        self.calls = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return self.embeddings[text]


def create_chunk(
    chunk_id: str,
    text: str,
) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        source_url="https://example.com/privacy",
        page_title="Privacy Policy",
        section_heading=None,
        text=text,
        retrieval_date="2026-10-04",
    )


def test_evidence_retriever_returns_most_relevant_chunk():
    chunks = [
        create_chunk(
            "chunk-001",
            "We collect your name and email address.",
        ),
        create_chunk(
            "chunk-002",
            "We use your personal data to send order confirmations.",
        ),
    ]

    embeddings = {
        "We collect your name and email address.": [1.0, 0.0],
        "We use your personal data to send order confirmations.": [
            0.0,
            1.0,
        ],
        "why the company uses customer data": [0.0, 0.9],
    }

    provider = FakeEmbeddingProvider(embeddings)

    retriever = EvidenceRetriever(
        embedding_provider=provider,
        chunks=chunks,
    )

    results = retriever.search(
        "why the company uses customer data",
        top_k=2,
    )

    assert results[0].chunk.chunk_id == "chunk-002"
    assert results[0].similarity > results[1].similarity
    

def test_evidence_retriever_embeds_chunks_once():
    chunks = [
        create_chunk(
            "chunk-001",
            "We collect your name.",
        ),
        create_chunk(
            "chunk-002",
            "We use your data for orders.",
        ),
    ]

    embeddings = {
        "We collect your name.": [1.0, 0.0],
        "We use your data for orders.": [0.0, 1.0],
        "first query": [1.0, 0.0],
        "second query": [0.0, 1.0],
    }

    provider = FakeEmbeddingProvider(embeddings)

    retriever = EvidenceRetriever(
        embedding_provider=provider,
        chunks=chunks,
    )

    retriever.search("first query")
    retriever.search("second query")

    assert provider.calls == [
        "We collect your name.",
        "We use your data for orders.",
        "first query",
        "second query",
    ]