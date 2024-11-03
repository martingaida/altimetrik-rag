from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    MONGODB_COLLECTION_NAME: str = os.getenv("MONGODB_COLLECTION_NAME", "")

    # Qdrant settings
    VECTOR_COLLECTION_NAME: str = os.getenv("VECTOR_COLLECTION_NAME", "")
    USE_QDRANT_CLOUD: bool = True
    QDRANT_CLUSTER_URL: str = os.getenv("QDRANT_CLUSTER_URL", "")   
    QDRANT_APIKEY: str | None = os.getenv("QDRANT_APIKEY", None)
    
    # OpenAI settings
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TEXT_EMBEDDING_MODEL: str = os.getenv("TEXT_EMBEDDING_MODEL", "")

    # Vector Embedding Settings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()