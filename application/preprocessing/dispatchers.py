from typing import List, Dict
from loguru import logger
from domain.base import VectorBaseDocument
from domain.types import DataCategory
from .chunking_data_handlers import EarningsCallChunkingHandler
from .embedding_data_handlers import EarningsCallEmbeddingHandler
from .cleaning_data_handlers import EarningsCallCleaningHandler

class CleaningDispatcher:
    @staticmethod
    def dispatch(document: Dict) -> VectorBaseDocument:
        try:
            handler = EarningsCallCleaningHandler()
            cleaned_document = handler.clean(document)
            logger.info("Document cleaned successfully")
            return cleaned_document
        except Exception as e:
            logger.error(f"Failed to clean document: {e}")
            raise

class ChunkingDispatcher:
    @staticmethod
    def dispatch(data_model: VectorBaseDocument) -> List[VectorBaseDocument]:
        if data_model.get_category() == DataCategory.EARNINGS_CALLS:
            handler = EarningsCallChunkingHandler()
            chunks = handler.chunk(data_model)
            logger.info(f"Document chunked successfully: {len(chunks)} chunks created")
            return chunks
        else:
            raise ValueError(f"Unsupported data category: {data_model.get_category()}")

class EmbeddingDispatcher:
    @staticmethod
    def dispatch(chunks: List[VectorBaseDocument]) -> List[VectorBaseDocument]:
        if not chunks:
            return []
            
        if chunks[0].get_category() == DataCategory.EARNINGS_CALLS:
            handler = EarningsCallEmbeddingHandler()
            embedded_chunks = handler.embed_batch(chunks)
            logger.info(f"Chunks embedded successfully: {len(embedded_chunks)} embeddings created")
            return embedded_chunks
        else:
            raise ValueError(f"Unsupported data category: {chunks[0].get_category()}")
