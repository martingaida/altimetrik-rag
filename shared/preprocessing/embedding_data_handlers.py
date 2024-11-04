from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from sentence_transformers import SentenceTransformer
from loguru import logger
from shared.domain.queries import EmbeddedLLMQuery, LLMQuery
from shared.domain.chunks import EarningsCallChunk
from shared.domain.embedded_chunks import EmbeddedECTChunk
from shared.domain.base.vector import VectorBaseDocument
from settings import settings

T = TypeVar('T')
U = TypeVar('U')

class EmbeddingDataHandler(ABC, Generic[T, U]):
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    @abstractmethod
    def map_model(self, data_model: T, embedding: List[float]) -> U:
        pass

    def embed_batch(self, data_models: List[T]) -> List[U]:
        if not data_models:
            return []
            
        try:
            texts = [model.content for model in data_models]
            embeddings = self.model.encode(texts).tolist()
            
            return [
                self.map_model(model, embedding)
                for model, embedding in zip(data_models, embeddings)
            ]
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise

class EarningsCallEmbeddingHandler(EmbeddingDataHandler[EarningsCallChunk, EmbeddedECTChunk]):
    def map_model(self, data_model: EarningsCallChunk, embedding: List[float]) -> EmbeddedECTChunk:
        return EmbeddedECTChunk(
            id=data_model.id,
            content=data_model.content,
            embedding=embedding,
            category=data_model.category,
            document_id=data_model.document_id,
            company_id=data_model.company_id,
            company_name=data_model.company_name,
            metadata={
                **data_model.metadata,
                "embedding_model": settings.EMBEDDING_MODEL_NAME,
                "embedding_size": len(embedding)
            }
        )

class QueriesEmbeddingHandler(EmbeddingDataHandler[EmbeddedLLMQuery, EmbeddedLLMQuery]):
    def map_model(self, data_model: EmbeddedLLMQuery, embedding: List[float]) -> EmbeddedLLMQuery:
        return EmbeddedLLMQuery(
            id=data_model.id,
            document_id=data_model.document_id,
            collection_name=data_model.collection_name,
            content=data_model.content,
            category=data_model.category,
            metadata=data_model.metadata,
            embedding=embedding
        )
