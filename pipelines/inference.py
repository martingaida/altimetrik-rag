from zenml import pipeline
from steps.inference.llm import generate_answer
from steps.retrieval.retriever import ContextRetriever
from shared.domain.embedded_chunks import EmbeddedChunk

@pipeline(enable_cache=False)
def inference_pipeline(query: str):
    """Pipeline for RAG-based inference."""
    
    # Step 1: Retrieve relevant context
    retriever = ContextRetriever(mock=False)
    documents = retriever.search(query, k=3)
    context = EmbeddedChunk.to_context(documents)
    
    # Step 2: Generate answer using LLM
    answer = generate_answer(query=query, context=context)
    
    return answer
