from typing import List, Dict
from zenml import step
from loguru import logger
from sentence_transformers import SentenceTransformer
from settings import settings

@step
def chunk_and_embed(documents: List[Dict]) -> List[Dict]:
    """Chunk and embed documents."""
    if not documents:
        logger.warning("No documents to process")
        return []
    
    # Initialize the embedding model
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    chunk_size = 1000
    overlap = 200
    
    processed_chunks = []
    
    for i, doc in enumerate(documents, 1):
        try:
            # Get document content and metadata
            content = str(doc.get('content', ''))
            metadata = doc.get('metadata', {})
            doc_id = str(doc.get('_id', f'doc_{i}'))
            
            logger.debug(f"Processing document with ID: {doc_id}")
            
            if doc_id == f'doc_{i}':
                logger.warning(f"Using fallback ID for document {i} - original _id not found")
            
            # Create chunks
            start = 0
            chunks = []
            
            while start < len(content):
                end = start + chunk_size
                chunk_text = content[start:end].strip()
                
                if chunk_text:
                    # Try to find a good breaking point
                    if end < len(content):
                        last_period = chunk_text.rfind('.')
                        last_newline = chunk_text.rfind('\n')
                        break_point = max(last_period, last_newline)
                        
                        if break_point > chunk_size // 2:  # Only break if we're past halfway
                            chunk_text = chunk_text[:break_point + 1]
                            end = start + break_point + 1
                    
                    # Create embedding
                    embedding = model.encode(chunk_text).tolist()
                    
                    # Create chunk document
                    chunk_doc = {
                        'text': chunk_text,
                        'embedding': embedding,
                        'metadata': {
                            'category': metadata.get('category', 'unknown'),
                            'chunk_index': len(chunks),
                            'original_id': doc_id,
                            'start_char': start,
                            'end_char': end
                        }
                    }
                    chunks.append(chunk_doc)
                
                # Move start position, accounting for overlap
                start = end - overlap
            
            processed_chunks.extend(chunks)
            logger.info(f"Processed document {i}: created {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process document {i}: {e}")
            continue
    
    logger.info(f"Total chunks created: {len(processed_chunks)}")
    return processed_chunks