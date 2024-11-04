from uuid import UUID
from pydantic import Field
from shared.domain.base import VectorBaseDocument
from shared.domain.types import DataCategory


class CleanedECTDocument(VectorBaseDocument):
    content: dict = Field(..., description="Contains 'presentation' and 'qa' sections")
    metadata: dict = Field(default_factory=dict)
    company_id: UUID
    company_name: str

    class Config:
        name = "cleaned_earnings_call_transcripts"
        category = DataCategory.EARNINGS_CALLS
