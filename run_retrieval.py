from loguru import logger
from shared.domain.queries import LLMQuery
from steps.retrieval.retriever import ContextRetriever

def test_retrieval():
    # Test query
    query = "What was Salesforce's revenue guidance for next quarter?"
    logger.info(f"\nTesting retrieval with query: {query}")
    
    try:
        # Create retriever
        retriever = ContextRetriever()
        
        # Get results
        results = retriever.search(query, k=3)
        
        # Print results
        logger.info("\nRetrieved chunks:")
        for i, chunk in enumerate(results, 1):
            logger.info(f"\n--- Chunk {i} ---")
            logger.info(f"Content: {chunk.content}")
            logger.info(f"Metadata: {chunk.metadata}")
            
    except Exception as e:
        logger.error(f"Error during retrieval test: {e}")
        raise

if __name__ == "__main__":
    test_retrieval()