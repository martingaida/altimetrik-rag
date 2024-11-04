from zenml import step
from model.inference import LLMInferenceOpenAI, InferenceExecutor
from loguru import logger

@step
def generate_answer(query: str, context: str) -> str:
    """Step to generate answer using LLM based on retrieved context."""
    logger.info("Generating answer using LLM")
    
    llm = LLMInferenceOpenAI()
    executor = InferenceExecutor(llm, query, context)
    answer = executor.execute()
    
    return answer