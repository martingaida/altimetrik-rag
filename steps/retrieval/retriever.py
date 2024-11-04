from loguru import logger
from shared.domain.embedded_chunks import EmbeddedChunk
from pipelines.retrieval import retrieval_pipeline

class ContextRetriever:
    def __init__(self, mock: bool = False) -> None:
        self.mock = mock

    def search(
        self,
        query: str,
        k: int = 3,
    ) -> list[EmbeddedChunk]:
        """Use the retrieval pipeline to get relevant documents"""
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
            # Return empty list if retrieval fails
            return []
