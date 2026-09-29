from regulatory_models import RegulatoryRequirement


requirement = RegulatoryRequirement(
    requirement_id="GDPR-ART12-001",
    source="GDPR",
    section="Articles 12-14",
    topic="transparency",
    requirement="Individuals must be informed about the purposes for which their personal data is processed.",
    effective_date=None,
    evidence_needed=[
        "Privacy notice describing purposes of processing"
    ],
)

print(requirement)
print()
print(requirement.topic)
print(requirement.evidence_needed)