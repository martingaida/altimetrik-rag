from typing import List, Dict
from zenml import step
from uuid import UUID
from loguru import logger

SALESFORCE_ID = UUID('12345678-1234-5678-1234-567812345678')
SALESFORCE_NAME = "Salesforce Inc."

@step
def clean_documents(
    documents: List[Dict],
) -> List[Dict]:
    """Structure the already cleaned documents for vector database storage."""
    cleaned_documents = []
    
    for doc in documents:
        try:
            content = doc.get("content", {})
            metadata = doc.get("metadata", {})
            original_id = doc.get("_id")
            
            if not isinstance(content, dict) or not all(k in content for k in ["presentation", "qa"]):
                logger.error(f"Invalid document structure: {doc.get('source', 'unknown')}")
                continue
                
            cleaned_documents.append({
                "_id": original_id,
                "content": {
                    "presentation": content["presentation"],
                    "qa": content["qa"]
                },
                "metadata": metadata,
                "company_id": SALESFORCE_ID,
                "company_name": SALESFORCE_NAME
            })
            
            logger.info(f"Processed document: {len(content['presentation']) + len(content['qa'])} chars total")
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            continue
    
    return cleaned_documents
