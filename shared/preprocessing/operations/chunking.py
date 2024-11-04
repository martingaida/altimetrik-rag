from typing import List
import re
from loguru import logger

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """Split text into chunks with overlap using sentence boundaries."""
    # First split by paragraphs to preserve structure
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        # Split paragraph into sentences
        sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_size = len(sentence)
            
            if current_size + sentence_size > chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    # Keep last few sentences for overlap
                    overlap_size = 0
                    overlap_chunk = []
                    for s in reversed(current_chunk):
                        if overlap_size + len(s) <= chunk_overlap:
                            overlap_chunk.insert(0, s)
                            overlap_size += len(s)
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_size = overlap_size
                else:
                    # Handle case where single sentence exceeds chunk_size
                    chunks.append(sentence)
                    current_chunk = []
                    current_size = 0
                    continue
                    
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks
