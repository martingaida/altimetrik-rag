from abc import ABC
from typing import Optional, Type, TypeVar, Any, Dict
from uuid import UUID
from loguru import logger
from pydantic import BaseModel, Field
from infrastructure.db.mongo import database
from domain.exceptions import ImproperlyConfigured

T = TypeVar("T", bound="NoSQLBaseDocument")

class NoSQLBaseDocument(BaseModel, ABC):
    id: UUID = Field(default_factory=UUID)
    
    class Config:
        name = "digital_data"  # Default collection name
        arbitrary_types_allowed = True
        
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Config") or not hasattr(cls.Config, "name"):
            raise ImproperlyConfigured(
                "Document should define a Config configuration class with the name of the collection."
            )
        return cls.Config.name
    
    @classmethod
    def bulk_find(cls: Type[T], **filter_options) -> list[T]:
        collection = database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            return [document for instance in instances if (document := cls.from_mongo(instance))]
        except Exception as e:
            logger.error(f"Failed to bulk find documents: {e}")
            raise

    @classmethod
    def from_mongo(cls: Type[T], data: Dict[str, Any]) -> Optional[T]:
        """Convert MongoDB document to Pydantic model."""
        if not data:
            return None
            
        mongo_id = data.pop("_id", None)
        if mongo_id:
            data["id"] = UUID(bytes=mongo_id.binary)
            
        return cls(**data)

    def to_mongo(self) -> Dict[str, Any]:
        """Convert Pydantic model to MongoDB document format."""
        data = self.dict(by_alias=True)
        if "id" in data:
            data["_id"] = data.pop("id")
        return data
