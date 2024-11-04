from abc import ABC, abstractmethod
from typing import List
from shared.domain.cleaned_documents import CleanedECTDocument
from shared.domain.chunks import EarningsCallChunk
from .operations.chunking import create_chunks
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
    def chunk(self, document: CleanedECTDocument) -> List[EarningsCallChunk]:
        pass

class EarningsCallChunkingHandler(ChunkingDataHandler):
    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 1000,
            "chunk_overlap": 100,
        }

    def chunk(self, document: CleanedECTDocument) -> List[EarningsCallChunk]:
        chunks = []
        
        # Handle both presentation and Q&A sections
        sections = [
            ("presentation", document.content["presentation"]),
            ("qa", document.content["qa"])
        ]
        
        for section_type, content in sections:
            # Clean the text first
            cleaned_content = clean_text(content)
            # Then chunk it
            text_chunks = create_chunks(
                cleaned_content, 
                chunk_size=self.metadata["chunk_size"], 
                chunk_overlap=self.metadata["chunk_overlap"]
            )
            
            for chunk in text_chunks:
                chunk_id = hashlib.md5(chunk.encode()).hexdigest()
                chunks.append(EarningsCallChunk(
                    id=UUID(chunk_id),
                    content=chunk,
                    category=document.get_category(),
                    document_id=document.id,
                    company_id=document.company_id,
                    company_name=document.company_name,
                    metadata={
                        **self.metadata,
                        "section": section_type,
                        **document.metadata
                    }
                ))
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks 