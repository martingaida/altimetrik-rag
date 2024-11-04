from typing import List, Dict, Any
from settings import settings
from shared.preprocessing.operations.cleaning import parse_pdf_date
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
        source = doc.get("source", "")
        creation_date = parse_pdf_date(metadata.get("creation_date", "")) or ""
        modification_date = parse_pdf_date(metadata.get("modification_date", "")) or ""

        if "/" in source:
            source = source.split("/")[-1]

        # Create transformed document
        transformed_doc = {
            "content": {
                "presentation": content.get("presentation", ""),
                "qa": content.get("qa", ""),
                "pages": [{"page": p["page"], "text": p["text"]} for p in pages]
            },
            "metadata": {
                "source": source,
                "type": "earnings_call",
                "document_type": "transcript",
                "company_id": settings.SALESFORCE_ID,
                "company_name": settings.SALESFORCE_NAME,
                "page_count": metadata.get("page_count", 0),
                "original_length": metadata.get("original_length", 0),
                "cleaned_length": metadata.get("cleaned_length", 0),
                "normalized_length": metadata.get("normalized_length", 0),
                "pdf_title": doc.get("title", ""),
                "pdf_author": metadata.get("author", ""),
                "pdf_creation_date": creation_date,
                "pdf_modification_date": modification_date
            }
        }
        
        logger.info(f"Transformed document {doc.get('source')}: "
                   f"Presentation: {len(content.get('presentation', ''))} chars, "
                   f"Q&A: {len(content.get('qa', ''))} chars")
        
        transformed_data.append(transformed_doc)
    
    return transformed_data