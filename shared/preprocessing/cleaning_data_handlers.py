from abc import ABC, abstractmethod
from typing import Dict
from loguru import logger
from shared.domain.cleaned_documents import CleanedECTDocument
from shared.preprocessing.operations.cleaning import clean_text

class CleaningDataHandler(ABC):
    @abstractmethod
    def clean(self, data_model) -> Dict:
        pass

class EarningsCallCleaningHandler(CleaningDataHandler):
    def clean(self, document: Dict) -> CleanedECTDocument:
        try:
            content = document.get("content", {})
            metadata = document.get("metadata", {})
            
            if not isinstance(content, dict) or not all(k in content for k in ["presentation", "qa"]):
                logger.error(f"Invalid document structure")
                raise ValueError("Document missing required sections")
            
            # Clean both sections
            cleaned_content = {
                "presentation": clean_text(content["presentation"]),
                "qa": clean_text(content["qa"])
            }
            
            return CleanedECTDocument(
                content=cleaned_content,
                metadata=metadata,
                company_id=document["company_id"],
                company_name=document["company_name"]
            )
            
        except Exception as e:
            logger.error(f"Failed to clean document: {e}")
            raise
