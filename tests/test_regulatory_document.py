from regai.regulatory_document import RegulatoryDocument
from regai.regulatory_models import RegulatoryRequirement


requirement = RegulatoryRequirement(
    source="European Union General Data Protection Regulation (GDPR)",
    section="Article 12",
    effective_date="2018-05-25",
    original_text=(
        "The controller shall take appropriate measures to provide "
        "any information referred to in Articles 13 and 14..."
    ),
    topic="Transparency and Communication with Data Subjects",
    interpretation=(
        "The organisation must provide information to data subjects "
        "in a concise, transparent, intelligible and accessible manner."
    ),
    evidence_needed=[
        "Privacy notices",
        "Data subject communications",
    ],
)


document = RegulatoryDocument(
    source="European Union",
    title="General Data Protection Regulation",
    publication_date="2016-04-27",
    effective_date="2018-05-25",
    requirements=[requirement],
)


print(document)
print()
print(document.requirements[0].original_text)
print()
print(document.requirements[0].interpretation)