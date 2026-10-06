from regai.evidence_source import (
    EvidenceSource,
    EvidenceSourceType,
)

import requests

from regai.evidence_processing import extract_text
from regai.evidence_source import (
    EvidenceSource,
    EvidenceSourceType,
)


def fetch_web_page(url: str) -> EvidenceSource:

    response = requests.get(
        url,
        timeout=10,
    )

    response.raise_for_status()

    content = extract_text(response.text)

    return EvidenceSource(
        source_type=EvidenceSourceType.WEB_PAGE,
        url=url,
        content=content,
    )