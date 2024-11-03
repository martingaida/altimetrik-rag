from typing import List, Dict
from zenml import step
from infrastructure.db.qdrant import QdrantClient
from settings import settings
from loguru import logger

@step
def load_to_vector_db(documents: List[Dict], collection_name: str = settings.VECTOR_COLLECTION_NAME) -> None:
    """Load documents into Qdrant vector database."""
    logger.info(f"Attempting to load {len(documents)} documents to vector database")
    
    if not documents:
        logger.warning("No documents to load into vector database")
        return
    
    try:
        # Initialize Qdrant client
        qdrant_client = QdrantClient()
        
        # Add documents using simplified API
        qdrant_client.add_documents(
            documents=documents,
            collection_name=collection_name
        )
        
        logger.info(f"Successfully loaded {len(documents)} documents to vector database")
        
    except Exception as e:
        logger.error(f"Failed to load documents to vector database: {e}")
        raise
    
    logger.info("Completed loading documents to vector database")
