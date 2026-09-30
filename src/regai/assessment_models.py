from enum import Enum

from pydantic import BaseModel


class AssessmentStatus(str, Enum):
    GREEN = "green"
    WARNING = "warning"
    RED = "red"
    NOT_ASSESSED = "not_assessed"


class RequirementEvidence(BaseModel):
    url: str
    observed_text: str
    retrieval_date: str


class RequirementAssessment(BaseModel):
    requirement_id: str
    status: AssessmentStatus
    explanation: str
    evidence: list[RequirementEvidence]