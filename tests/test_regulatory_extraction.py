from regai.regulatory_extraction import extract_requirements


def test_extracts_independently_assessable_requirements():
    source_text = """
Article 13

Where personal data relating to a data subject are collected from the data subject,
the controller shall provide the following information:

(a) the identity and the contact details of the controller;

(b) the purposes of the processing for which the personal data are intended;

(c) the recipients or categories of recipients of the personal data, if any.
"""

    requirements = extract_requirements(
        source_text=source_text,
        source="Test Regulation",
        effective_date="2026-01-01",
    )

    assert len(requirements) == 3

    sections = [requirement.section for requirement in requirements]

    assert "13(a)" in sections
    assert "13(b)" in sections
    assert "13(c)" in sections