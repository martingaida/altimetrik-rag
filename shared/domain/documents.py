from pydantic import UUID4, Field, BaseModel
from shared.domain.base import NoSQLBaseDocument
from shared.domain.types import DataCategory
from typing import Dict, Any


class EarningsCallDocument(NoSQLBaseDocument):
    content: str
    metadata: dict = Field(default_factory=dict)

    class Config:
        name = DataCategory.EARNINGS_CALLS


class VectorSearchResult(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float | None = None

    @property
    def content(self) -> str:
        """Alias for text field to maintain consistency"""
        return self.text
