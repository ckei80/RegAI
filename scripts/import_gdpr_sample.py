from pathlib import Path

from regai.config import get_settings_path
from regai.regulatory_ingestion import load_text_file
from regai.regulatory_processing import process_regulatory_source
from regai.regulatory_store import RegulatoryStore


SOURCE_ID = "gdpr_sample"
SOURCE_PATH = Path("data/sample/gdpr_sample.txt")
TITLE = "General Data Protection Regulation"
EFFECTIVE_DATE = "2018-05-25"


def main() -> None:
    store_path = get_settings_path().parent / "regulations.json"
    store = RegulatoryStore(store_path)

    existing_document = store.get_document(SOURCE_ID)

    if existing_document is not None:
        print(f"Regulatory document already exists: {existing_document.title}")
        print(f"Store location: {store_path}")
        print("Skipping extraction to avoid another LLM call.")
        return

    source = load_text_file(
        path=str(SOURCE_PATH),
        source_id=SOURCE_ID,
    )

    print(f"Processing: {TITLE}")
    print("Extracting regulatory requirements using the configured LLM...")

    document = process_regulatory_source(
        source=source,
        title=TITLE,
        effective_date=EFFECTIVE_DATE,
    )

    store.save_document(document)

    print("\nRegulatory document saved successfully.")
    print(f"Title: {document.title}")
    print(f"Source ID: {document.source}")
    print(f"Requirements extracted: {len(document.requirements)}")
    print(f"Effective date: {document.effective_date}")
    print(f"Store location: {store_path}")


if __name__ == "__main__":
    main()