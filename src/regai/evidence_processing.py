from bs4 import BeautifulSoup
from regai.evidence_models import EvidenceChunk
from regai.evidence_source import EvidenceSource


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style"]):
        element.decompose()

    return soup.get_text(
        separator=" ",
        strip=True,
    )

def extract_page_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")

    if title is None:
        return None

    text = title.get_text(" ", strip=True)

    return text or None

def extract_sections(html: str) -> list[dict[str, str | None]]:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "nav"]):
        element.decompose()

    sections = []
    current_heading = None
    current_parts = []

    for element in soup.find_all(
        ["h2", "h3", "h4", "h5", "h6", "p", "li"]
    ):
        text = element.get_text(" ", strip=True)

        if not text:
            continue

        if element.name.startswith("h"):
            if current_parts:
                sections.append(
                    {
                        "heading": current_heading,
                        "text": " ".join(current_parts),
                    }
                )

            current_heading = text
            current_parts = []
        else:
            current_parts.append(text)

    if current_parts:
        sections.append(
            {
                "heading": current_heading,
                "text": " ".join(current_parts),
            }
        )
    
    return sections

def create_evidence_chunks(
    html: str,
    url: str,
    retrieval_date: str,
) -> list[EvidenceChunk]:
    page_title = extract_page_title(html)
    sections = extract_sections(html)

    chunks = []

    for index, section in enumerate(sections, start=1):
        chunks.append(
            EvidenceChunk(
                chunk_id=f"chunk-{index:03d}",
                source_url=url,
                page_title=page_title,
                section_heading=section["heading"],
                text=section["text"],
                retrieval_date=retrieval_date,
            )
        )

    return chunks

def process_evidence_source(
    source: EvidenceSource,
    retrieval_date: str,
) -> list[EvidenceChunk]:
    return create_evidence_chunks(
        html=source.content,
        url=source.url,
        retrieval_date=retrieval_date,
    )