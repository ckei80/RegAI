from pathlib import Path

from regai.regulatory_source import RegulatorySource, SourceType


def load_text_file(
    path: str,
    source_id: str,
) -> RegulatorySource:

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Regulatory source file not found: {path}"
        )

    content = file_path.read_text(encoding="utf-8")

    return RegulatorySource(
        source_id=source_id,
        source_type=SourceType.TEXT,
        location=str(file_path),
        content=content,
    )