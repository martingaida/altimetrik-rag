from typing import List, Optional, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from loguru import logger
from sentence_transformers import SentenceTransformer
from settings import settings
from domain.types import DataCategory
from infrastructure.db.qdrant import connection

T = TypeVar("T", bound="VectorBaseDocument")

class VectorBaseDocument(BaseModel):
    id: UUID
    collection_name: str
    
    @classmethod
    def _get_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Get embeddings using SentenceTransformer."""
        try:
            model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            return model.encode(texts).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    @classmethod
    def create_collection(cls) -> None:
        """Create a Qdrant collection if it doesn't exist."""
        if not connection.collection_exists(cls.collection_name):
            connection.create_collection(
                collection_name=cls.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,  # 384 for all-MiniLM-L6-v2
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {cls.collection_name}")

    def to_vector(self) -> PointStruct:
        """Convert document to vector format for storage."""
        embedding = self._get_embeddings([self.get_text_for_embedding()])[0]
        return PointStruct(
            id=str(self.id),
            payload=self.dict(),
            vector=embedding
        )

    def get_text_for_embedding(self) -> str:
        """Override this method to specify which text should be embedded."""
        raise NotImplementedError

    def save(self) -> None:
        """Save document to vector database."""
        try:
            # Ensure collection exists
            self.create_collection()
            
            # Convert to vector format
            point = self.to_vector()
            logger.debug(f"Converting document {self.id} to vector format")
            
            # Save to Qdrant
            connection.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Saved document {self.id} to Qdrant collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to save document {self.id}: {e}")
            raise
