from typing import List, Dict, Any
from loguru import logger
from settings import settings


def flatten(nested_list: list) -> list:
    """Flatten a nested list."""
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten(item))
        else:
            flattened.append(item)
    return flattened


def count_tokens(text: str) -> int:
    """Estimate token count using simple heuristic."""
    # OpenAI's tokenizer typically splits on spaces and punctuation
    # This is a rough estimate - OpenAI's API will handle actual tokenization
    return len(text.split())


def chunk_text(text: str, max_tokens: int = 8000) -> List[str]:
    """Split text into chunks that fit within token limit."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    sentences = text.split('. ')
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        
        if current_length + sentence_tokens > max_tokens:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_length = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_length += sentence_tokens
    
    # Add any remaining text
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks


def format_document_metadata(metadata: Dict[str, Any]) -> str:
    """Format document metadata into a string."""
    formatted = []
    for key, value in metadata.items():
        if value:
            formatted.append(f"{key}: {value}")
    return "\n".join(formatted)
