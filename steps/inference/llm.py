from zenml import step
from loguru import logger
from model.inference.inference import LLMInferenceOpenAI, InferenceExecutor


@step
def generate_answer(query: str, context: str) -> str:
    """Generate answer using LLM based on retrieved context"""
    try:
        logger.info("Initializing LLM for answer generation")
        
        # Initialize LLM
        llm = LLMInferenceOpenAI()
        
        # Create executor
        executor = InferenceExecutor(llm=llm, query=query, context=context)
        
        # Generate answer
        logger.info("Generating answer...")
        answer = executor.execute()
        
        if not answer:
            raise ValueError("LLM returned empty answer")
            
        logger.info("Successfully generated answer")
        return answer
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return f"Sorry, I encountered an error while generating the answer: {str(e)}"