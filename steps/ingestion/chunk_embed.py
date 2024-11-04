from typing import List, Dict
from zenml import step
from loguru import logger
from sentence_transformers import SentenceTransformer
from shared.preprocessing.operations.chunking import create_chunks
from shared.preprocessing.operations.chunk_tagging import tag_chunk
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
            content = doc.get('content', '')
            presentation = str(content.get('presentation', ''))
            qa = str(content.get('qa', ''))
            metadata = doc.get('metadata', {})
            doc_id = str(doc.get('_id', f'doc_{i}'))
            
            logger.debug(f"Processing document with ID: {doc_id}")
            
            if doc_id == f'doc_{i}':
                logger.warning(f"Using fallback ID for document {i} - original _id not found")
            
            # Process each section using chunk_text
            for text_type, text in [("presentation", presentation), ("qa", qa)]:
                if not text.strip():
                    continue
                    
                # Use chunk_text function
                chunks = create_chunks(text, chunk_size=chunk_size, chunk_overlap=overlap)
                
                for chunk_index, chunk in enumerate(chunks):
                    # Create embedding
                    embedding = model.encode(chunk).tolist()
                    
                    # Create chunk document
                    chunk_doc = {
                        'text': chunk,
                        'embedding': embedding,
                        'metadata': {
                            **metadata,  # Spread the original document metadata
                            'tags': tag_chunk(chunk),
                            'chunk_index': chunk_index,
                            'original_id': doc_id,
                            'section': text_type,
                            'total_chunks': len(chunks)
                        }
                    }
                    processed_chunks.append(chunk_doc)
                
                logger.info(f"Processed {text_type} section of document {i}: created {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process document {i}: {e}")
            continue
    
    logger.info(f"Total chunks created: {len(processed_chunks)}")
    return processed_chunks