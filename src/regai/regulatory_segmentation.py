import re

from pydantic import BaseModel


class SourceSegment(BaseModel):
    segment_id: str
    section: str
    original_text: str


def segment_regulatory_text(source_text: str) -> list[SourceSegment]:
    article_pattern = re.compile(
        r"(?m)^Article\s+(\d+)\b.*$"
    )

    article_matches = list(article_pattern.finditer(source_text))

    if not article_matches:
        raise ValueError("Could not find an article heading.")

    segments = []

    for article_index, article_match in enumerate(article_matches):
        article_number = article_match.group(1)

        article_start = article_match.end()

        if article_index + 1 < len(article_matches):
            article_end = article_matches[article_index + 1].start()
        else:
            article_end = len(source_text)

        article_text = source_text[article_start:article_end]

        clause_pattern = re.compile(
            r"(?m)^(\([a-z]\))\s+"
        )

        clause_matches = list(clause_pattern.finditer(article_text))

        for clause_index, clause_match in enumerate(clause_matches):
            clause = clause_match.group(1)

            clause_start = clause_match.start()

            if clause_index + 1 < len(clause_matches):
                clause_end = clause_matches[clause_index + 1].start()
            else:
                clause_end = len(article_text)

            original_text = article_text[
                clause_start:clause_end
            ].strip()

            segment_id = (
                f"ART{article_number}-{clause[1].upper()}"
            )

            segments.append(
                SourceSegment(
                    segment_id=segment_id,
                    section=f"{article_number}{clause}",
                    original_text=original_text,
                )
            )

    return segments