from abc import ABC
from pydantic import UUID4, Field
from shared.domain.documents import VectorSearchResult
from shared.domain.types import DataCategory
from shared.domain.chunks import Chunk
from typing import List


class EmbeddedChunk(Chunk):
    embedding: list[float]

    @staticmethod
    def to_context(documents: List[VectorSearchResult]) -> str:
        """Convert a list of VectorSearchResult objects to a context string"""
        if not documents:
            return ""
            
        # Join all document texts with newlines and section markers
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Section {i}]\n{doc.text}\n")
            
        return "\n".join(context_parts)


class EmbeddedECTChunk(EmbeddedChunk):
    class Config:
        name = "embedded_ect_chunk"
        category = DataCategory.EARNINGS_CALLS
        use_vector_index = True