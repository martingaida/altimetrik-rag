from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from sentence_transformers import SentenceTransformer
from loguru import logger
from domain.chunks import EarningsCallChunk
from domain.embedded_chunks import EmbeddedEarningsCallChunk
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

class EarningsCallEmbeddingHandler(EmbeddingDataHandler[EarningsCallChunk, EmbeddedEarningsCallChunk]):
    def map_model(self, data_model: EarningsCallChunk, embedding: List[float]) -> EmbeddedEarningsCallChunk:
        return EmbeddedEarningsCallChunk(
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
