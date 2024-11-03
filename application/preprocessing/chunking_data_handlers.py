from abc import ABC, abstractmethod
from typing import List
from domain.cleaned_documents import CleanedECTDocument
from domain.chunks import EarningsCallChunk
from .operations.chunking import chunk_text
from .operations.cleaning import clean_text
import hashlib
from uuid import UUID
from loguru import logger

class ChunkingDataHandler(ABC):
    @property
    @abstractmethod
    def metadata(self) -> dict:
        pass

    @abstractmethod
    def chunk(self, data_model) -> List:
        pass

class EarningsCallChunkingHandler(ChunkingDataHandler):
    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 1000,
            "chunk_overlap": 100,
        }

    def chunk(self, data_model: CleanedECTDocument) -> List[EarningsCallChunk]:
        chunks = []
        
        # Handle both presentation and Q&A sections
        sections = [
            ("presentation", data_model.content["presentation"]),
            ("qa", data_model.content["qa"])
        ]
        
        for section_type, content in sections:
            # Clean the text first
            cleaned_content = clean_text(content)
            # Then chunk it
            text_chunks = chunk_text(
                cleaned_content, 
                chunk_size=self.metadata["chunk_size"], 
                chunk_overlap=self.metadata["chunk_overlap"]
            )
            
            for chunk in text_chunks:
                chunk_id = hashlib.md5(chunk.encode()).hexdigest()
                chunks.append(EarningsCallChunk(
                    id=UUID(chunk_id),
                    content=chunk,
                    category=data_model.get_category(),
                    document_id=data_model.id,
                    company_id=data_model.company_id,
                    company_name=data_model.company_name,
                    metadata={
                        **self.metadata,
                        "section": section_type,
                        **data_model.metadata
                    }
                ))
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks 