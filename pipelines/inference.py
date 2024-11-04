from zenml import pipeline
from steps.inference.llm import generate_answer
from steps.inference.context import prepare_context
from steps.retrieval.retriever import retrieve_context
from loguru import logger

@pipeline(enable_cache=False)
def inference_pipeline(query: str) -> str:
    """Pipeline for RAG-based inference."""
    try:
        logger.info(f"Starting inference pipeline for query: {query}")
        
        # Step 1: Retrieve relevant context
        documents = retrieve_context(query=query, k=5)
        
        # Step 2: Prepare context
        context = prepare_context(documents=documents)
        
        # Step 3: Generate answer using LLM
        answer = generate_answer(query=query, context=context)
        
        return answer
        
    except Exception as e:
        logger.error(f"Error in inference pipeline: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}"
