from pydantic import UUID4, Field, BaseModel
from loguru import logger
from uuid import uuid4
from settings import settings
from shared.domain.base.vector import VectorBaseDocument
from shared.domain.types import DataCategory


class VectorQuery(VectorBaseDocument):
    content: str
    embedding: list[float]

    class Config:
        category = DataCategory.QUERIES

    @classmethod
    def from_str(cls, query: str) -> "VectorQuery":
        return VectorQuery(content=query.strip("\n "))

    def replace_content(self, new_content: str) -> "VectorQuery":
        return VectorQuery(
            id=self.id,
            content=new_content,
            embedding=self.embedding,
        )


class LLMQuery(BaseModel):
    content: str
    category: str | None = None
    metadata: dict = Field(default_factory=dict)

    @classmethod
    def from_str(cls, query: str) -> "LLMQuery":
        return cls(content=query.strip("\n "))

    def replace_content(self, new_content: str) -> "LLMQuery":
        return LLMQuery(
            content=new_content,
            category=self.category,
            metadata=self.metadata,
        )

    def add_metadata(self, metadata_query: "LLMQuery") -> "EmbeddedLLMQuery":
        generated_id = uuid4()
        result = EmbeddedLLMQuery(
            id=generated_id,
            document_id=str(generated_id),
            collection_name=settings.VECTOR_COLLECTION_NAME,
            content=self.content,
            category=DataCategory.QUERIES.value,
            metadata=metadata_query.metadata,
            embedding=[]
        )
        logger.info(f"Created EmbeddedLLMQuery: {result}")
        return result


class EmbeddedLLMQuery(LLMQuery, VectorBaseDocument):
    embedding: list[float]
    document_id: str

    def get_category(self) -> str:
        return self.category or DataCategory.QUERIES.value
