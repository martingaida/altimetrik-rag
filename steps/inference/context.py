from zenml import step
from shared.domain.embedded_chunks import EmbeddedChunk
from shared.domain.documents import VectorSearchResult
from typing import List

@step
def prepare_context(documents: List[VectorSearchResult]) -> str:
    """Convert retrieved documents into context string"""
    if not documents:
        return ""
        
    # Join all document texts with newlines and section markers
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"[Section {i}]\n{doc.text}\n")
        
    return "\n".join(context_parts) 