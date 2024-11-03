import hashlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from domain.chunks import Chunk, EarningsCallChunk
from domain.cleaned_documents import (
    CleanedECTDocument
)

from .operations import chunk_article, chunk_text

CleanedDocumentT = TypeVar("CleanedDocumentT", bound=CleanedDocument)
ChunkT = TypeVar("ChunkT", bound=Chunk)


class ChunkingDataHandler(ABC, Generic[CleanedDocumentT, ChunkT]):
    """
    Abstract class for all Chunking data handlers.
    All data transformations logic for the chunking step is done here
    """

    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 500,
            "chunk_overlap": 50,
        }

    @abstractmethod
    def chunk(self, data_model: CleanedDocumentT) -> list[ChunkT]:
        pass


class EarningsCallChunkingHandler(ChunkingDataHandler[CleanedECTDocument, EarningsCallChunk]):
    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 1000,
            "chunk_overlap": 100,
        }

    def chunk(self, data_model: CleanedECTDocument) -> list[EarningsCallChunk]:
        data_models_list = []
        
        # Handle both presentation and Q&A sections
        sections = [
            ("presentation", data_model.content["presentation"]),
            ("qa", data_model.content["qa"])
        ]
        
        for section_type, content in sections:
            chunks = chunk_text(
                content, 
                chunk_size=self.metadata["chunk_size"], 
                chunk_overlap=self.metadata["chunk_overlap"]
            )
            
            for chunk in chunks:
                chunk_id = hashlib.md5(chunk.encode()).hexdigest()
                model = EarningsCallChunk(
                    id=UUID(chunk_id, version=4),
                    content=chunk,
                    category="earnings_call_transcript",
                    document_id=data_model.id,
                    company_id=data_model.company_id,
                    company_name=data_model.company_name,
                    metadata={
                        **self.metadata,
                        "section": section_type,
                        "fiscal_quarter": data_model.fiscal_quarter,
                        "fiscal_year": data_model.fiscal_year,
                        "earnings_date": data_model.earnings_date,
                        "speakers": data_model.speakers,
                    },
                )
                data_models_list.append(model)
        
        return data_models_list