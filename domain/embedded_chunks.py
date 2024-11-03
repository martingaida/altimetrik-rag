from abc import ABC
from pydantic import UUID4, Field
from domain.base import VectorBaseDocument
from domain.types import DataCategory
from domain.chunks import Chunk


class EmbeddedChunk(Chunk):
    embedding: list[float]


class EmbeddedEarningsCallChunk(EmbeddedChunk):
    class Config:
        name = "embedded_ect_chunk"
        category = DataCategory.EARNINGS_CALLS
        use_vector_index = True