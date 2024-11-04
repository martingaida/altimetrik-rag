from abc import ABC
from pydantic import UUID4, Field
from shared.domain.base import VectorBaseDocument
from shared.domain.types import DataCategory
from shared.domain.chunks import Chunk


class EmbeddedChunk(Chunk):
    embedding: list[float]


class EmbeddedECTChunk(EmbeddedChunk):
    class Config:
        name = "embedded_ect_chunk"
        category = DataCategory.EARNINGS_CALLS
        use_vector_index = True