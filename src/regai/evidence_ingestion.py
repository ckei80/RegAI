import requests

from regai.evidence_source import (
    EvidenceSource,
    EvidenceSourceType,
)


def fetch_web_page(url: str) -> EvidenceSource:
    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "RegAI/0.1",
        },
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if "text/html" not in content_type:
        raise ValueError(
            "The URL did not return an HTML page. "
            "PDF and other document formats are not supported yet."
        )

    return EvidenceSource(
        source_type=EvidenceSourceType.WEB_PAGE,
        url=response.url,
        content=response.text,
    )
