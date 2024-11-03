from typing import List, Dict, Any
from zenml import step
from loguru import logger

@step
def transform_transcript(
    raw_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Transform the normalized data for MongoDB storage."""
    transformed_data = []
    
    for doc in raw_data:
        content = doc.get("content", {})
        metadata = doc.get("metadata", {})
        pages = doc.get("pages", [])
        
        # Create transformed document
        transformed_doc = {
            "content": {
                "presentation": content.get("presentation", ""),
                "qa": content.get("qa", ""),
                "pages": [{"page": p["page"], "text": p["text"]} for p in pages]
            },
            "metadata": {
                "source": doc.get("source", ""),
                "type": "earnings_call",
                "page_count": metadata.get("page_count", 0),
                "original_length": metadata.get("original_length", 0),
                "cleaned_length": metadata.get("cleaned_length", 0),
                "normalized_length": metadata.get("normalized_length", 0),
                "pdf_title": metadata.get("pdf_title", ""),
                "pdf_author": metadata.get("pdf_author", ""),
                "pdf_creation_date": metadata.get("pdf_creation_date", ""),
                "pdf_modification_date": metadata.get("pdf_modification_date", "")
            }
        }
        
        logger.info(f"Transformed document {doc.get('source')}: "
                   f"Presentation: {len(content.get('presentation', ''))} chars, "
                   f"Q&A: {len(content.get('qa', ''))} chars")
        
        transformed_data.append(transformed_doc)
    
    return transformed_data