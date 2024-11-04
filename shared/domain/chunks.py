from abc import ABC
from pydantic import UUID4, Field
from shared.domain.base import VectorBaseDocument
from shared.domain.types import DataCategory


class Chunk(VectorBaseDocument, ABC):
    content: str
    category: str
    document_id: UUID4
    company_id: UUID4
    company_name: str
    metadata: dict = Field(default_factory=dict)


class EarningsCallChunk(Chunk):
    class Config:
        name = "ect_chunk"
        category = DataCategory.EARNINGS_CALLS
        use_vector_index = True