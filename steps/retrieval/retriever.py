from zenml import step
from loguru import logger
from shared.domain.documents import VectorSearchResult
from pipelines.retrieval import retrieval_pipeline
from typing import List

@step
def retrieve_context(query: str, k: int = 3) -> List[VectorSearchResult]:
    """Retrieve relevant context for the query"""
    try:
        # Get documents from retrieval pipeline
        documents = retrieval_pipeline(query)
        
        # Take top k documents
        if k and len(documents) > k:
            documents = documents[:k]
            
        logger.info(f"Retrieved {len(documents)} documents successfully")
        return documents
            
    except Exception as e:
        logger.error(f"Error in retrieval: {e}")
        return []
