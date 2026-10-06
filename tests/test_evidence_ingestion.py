from unittest.mock import patch

from regai.evidence_ingestion import fetch_web_page
from regai.evidence_source import EvidenceSourceType


@patch("regai.evidence_ingestion.requests.get")
def test_fetch_web_page_returns_processed_content(mock_get):

    mock_get.return_value.status_code = 200
    mock_get.return_value.text = """
        <html>
            <body>
                <h1>Privacy Policy</h1>
                <p>We collect your email address.</p>
                <script>
                    console.log("ignore this");
                </script>
            </body>
        </html>
    """

    source = fetch_web_page(
        "https://example.com/privacy"
    )

    assert source.source_type == EvidenceSourceType.WEB_PAGE
    assert source.url == "https://example.com/privacy"

    assert "Privacy Policy" in source.content
    assert "We collect your email address." in source.content
    assert "console.log" not in source.content