from loguru import logger
from fastapi.testclient import TestClient
from steps.inference_api import app

def test_simple_rag(query: str):
    """Test the RAG pipeline through the API endpoint"""
    client = TestClient(app)
    
    # Make request to endpoint
    response = client.post(
        "/rag",
        json={"query": query}
    )
    
    # Log results
    logger.info("\n" + "="*80)
    logger.info(f"QUERY: {query}")
    logger.info("FINAL ANSWER:")
    logger.info(response.json()["answer"])
    logger.info("="*80 + "\n")
        
    return response.json()["answer"]

if __name__ == "__main__":
    # Test query
    query = "What was Salesforce's revenue guidance for next quarter?"
    
    try:
        answer = test_simple_rag(query)
    except Exception as e:
        logger.error(f"Error during RAG execution: {e}")