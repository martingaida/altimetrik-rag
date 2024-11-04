from loguru import logger
from fastapi.testclient import TestClient
from steps.inference_api import app

def test_simple_rag(query: str):
    """Test the RAG pipeline through the API endpoint"""
    client = TestClient(app)
    
    try:
        # Make request to endpoint
        response = client.post(
            "/rag",
            json={"query": query}
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Get response data
        data = response.json()
        
        if "answer" not in data:
            raise ValueError("Response missing answer field")
            
        # Log results
        logger.info("\n" + "="*80)
        logger.info(f"QUERY: {query}")
        logger.info("FINAL ANSWER:")
        logger.info(data["answer"])
        logger.info("="*80 + "\n")
            
        return data["answer"]
        
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
        if response:
            logger.error(f"Response status: {response.status_code}")
            logger.error(f"Response body: {response.text}")
        raise

if __name__ == "__main__":
    # Test query
    query = "When was the most recent earnings call?"
    
    try:
        answer = test_simple_rag(query)
    except Exception as e:
        logger.error(f"Error during RAG execution: {e}")