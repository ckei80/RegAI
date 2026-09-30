from pathlib import Path

from regai.regulatory_extraction import extract_requirements


source_file = Path("data/sample/gdpr_sample.txt")
source_text = source_file.read_text(encoding="utf-8")

requirements = extract_requirements(
    source_text,
    source="European Union General Data Protection Regulation (GDPR)",
    effective_date="2018-05-25",
)

for requirement in requirements:
    print("\n--- Requirement ---")
    print(requirement)