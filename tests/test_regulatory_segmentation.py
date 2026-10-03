from regai.regulatory_segmentation import segment_regulatory_text


def test_segments_lettered_regulatory_clauses():
    source_text = """
Article 13

Where personal data relating to a data subject are collected from the data subject,
the controller shall provide the following information:

(a) the identity and the contact details of the controller;

(b) the purposes of the processing for which the personal data are intended;

(c) the recipients or categories of recipients of the personal data, if any.
"""

    segments = segment_regulatory_text(source_text)

    assert len(segments) == 3

    assert segments[0].segment_id == "ART13-A"
    assert segments[0].section == "13(a)"
    assert (
        segments[0].original_text
        == "(a) the identity and the contact details of the controller;"
    )

    assert segments[1].segment_id == "ART13-B"
    assert segments[2].segment_id == "ART13-C"