from regai.evidence_processing import (
    create_evidence_chunks,
    extract_page_title,
    extract_sections,
    extract_text,
    process_evidence_source,
)

from regai.evidence_source import (
    EvidenceSource,
    EvidenceSourceType,
)


def test_extract_text_removes_scripts_and_styles():

    html = """
    <html>
        <head>
            <style>
                body { color: red; }
            </style>
        </head>
        <body>
            <h1>Privacy Policy</h1>
            <p>We collect your email address.</p>
            <script>
                console.log("ignore this");
            </script>
        </body>
    </html>
    """

    text = extract_text(html)

    assert "Privacy Policy" in text
    assert "We collect your email address." in text
    assert "color: red" not in text
    assert 'console.log("ignore this")' not in text

def test_extract_page_title_returns_h1():
    html = """
        <html>
            <body>
                <h1>Privacy Policy</h1>
                <h2>How we use your information</h2>
                <p>We use your email for order confirmations.</p>
            </body>
        </html>
    """

    assert extract_page_title(html) == "Privacy Policy"

def test_extract_page_title_returns_none_when_missing():
    html = """
        <html>
            <body>
                <h2>How we use your information</h2>
                <p>We use your email for order confirmations.</p>
            </body>
        </html>
    """

    assert extract_page_title(html) is None

def test_extract_sections_preserves_headings_and_content():
    html = """
        <html>
            <body>
                <h1>Privacy Policy</h1>

                <h2>How we use your information</h2>
                <p>We use your email for order confirmations.</p>
                <p>We also use it for marketing.</p>

                <h2>Who we share information with</h2>
                <p>We share information with payment providers.</p>

                <script>
                    console.log("ignore this");
                </script>
            </body>
        </html>
    """

    sections = extract_sections(html)

    assert sections == [
        {
            "heading": "How we use your information",
            "text": (
                "We use your email for order confirmations. "
                "We also use it for marketing."
            ),
        },
        {
            "heading": "Who we share information with",
            "text": "We share information with payment providers.",
        },
    ]

def test_create_evidence_chunks():
    html = """
        <html>
            <body>
                <h1>Privacy Policy</h1>

                <h2>How we use your information</h2>
                <p>We use your email for order confirmations.</p>
                <p>We also use it for marketing.</p>

                <h2>Who we share information with</h2>
                <p>We share information with payment providers.</p>
            </body>
        </html>
    """

    chunks = create_evidence_chunks(
        html=html,
        url="https://example.com/privacy",
        retrieval_date="2026-10-04",
    )

    assert len(chunks) == 2

    assert chunks[0].chunk_id == "chunk-001"
    assert chunks[0].source_url == "https://example.com/privacy"
    assert chunks[0].page_title == "Privacy Policy"
    assert chunks[0].section_heading == "How we use your information"
    assert chunks[0].text == (
        "We use your email for order confirmations. "
        "We also use it for marketing."
    )

    assert chunks[1].chunk_id == "chunk-002"
    assert chunks[1].section_heading == "Who we share information with"

def test_process_evidence_source_creates_chunks():
    source = EvidenceSource(
        source_type=EvidenceSourceType.WEB_PAGE,
        url="https://example.com/privacy",
        content="""
            <html>
                <body>
                    <h1>Privacy Policy</h1>

                    <h2>How we use your information</h2>
                    <p>We use your email for order confirmations.</p>
                </body>
            </html>
        """,
    )

    chunks = process_evidence_source(
        source=source,
        retrieval_date="2026-10-04",
    )

    assert len(chunks) == 1
    assert chunks[0].source_url == "https://example.com/privacy"
    assert chunks[0].page_title == "Privacy Policy"
    assert chunks[0].section_heading == "How we use your information"
    assert chunks[0].text == (
        "We use your email for order confirmations."
    )