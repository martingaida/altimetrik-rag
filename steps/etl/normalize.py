from typing import List, Dict, Any
from zenml import step
from loguru import logger
import re

class TranscriptNormalizer:
    @staticmethod
    def normalize_case(text: str) -> str:
        """Convert text to lowercase for consistency."""
        return text.lower()

    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """Standardize punctuation and whitespace."""
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\s*([.,?!:;])\s*', r'\1 ', text)  # Ensure single space after punctuation
        return text.strip()

    @staticmethod
    def normalize_numbers(text: str) -> str:
        """Standardize common financial expressions like 'million' or 'billion'."""
        text = re.sub(r'\b(\d+)\s?million\b', r'\1,000,000', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(\d+)\s?billion\b', r'\1,000,000,000', text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def normalize_titles(text: str) -> str:
        """Replace job titles with common abbreviations."""
        title_mappings = {
            r'\bchief executive officer\b': 'CEO',
            r'\bchief financial officer\b': 'CFO',
            r'\bchief operating officer\b': 'COO',
            r'\bchief technology officer\b': 'CTO',
            r'\bexecutive vice president\b': 'EVP',
            r'\bsenior vice president\b': 'SVP',
            r'\bvice president\b': 'VP',
            r'\bmanaging director\b': 'MD'
        }
        
        for full_title, abbrev in title_mappings.items():
            text = re.sub(full_title, abbrev, text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def normalize_roles(text: str) -> str:
        """Standardize and format roles like 'Operator', 'Analyst', and 'Moderator'."""
        role_mappings = {
            r'\boperator\b': 'Operator:',
            r'\banalyst\b': 'Analyst:',
            r'\bmoderator\b': 'Moderator:',
            r'\bpresenter\b': 'Presenter:',
            r'\bceo\b': 'CEO:',
            r'\bcfo\b': 'CFO:'
        }
        
        for role, standardized_role in role_mappings.items():
            text = re.sub(role, standardized_role, text, flags=re.IGNORECASE)
        
        # Remove operator instructions (e.g., "Operator Instructions")
        text = re.sub(r'\bOperator Instructions\b', '', text, flags=re.IGNORECASE)
        
        return text


    @staticmethod
    def normalize_abbreviations(text: str) -> str:
        """Standardize common financial abbreviations and quarter abbreviations."""
        # First handle fiscal year patterns with numbers
        text = re.sub(r'\bfy(\d{2,4})\b', r'fiscal year \1', text, flags=re.IGNORECASE)
        text = re.sub(r'fiscal year (\d{2})(?!\d{2})\b', r"fiscal year '\1", text)
        text = re.sub(r'fiscal year (\d{4})\b', r"fiscal year '\1", text)
        
        # Handle quarter abbreviations first (before other abbreviations)
        quarter_mappings = {
            r'\bq1\b': 'first quarter',
            r'\bq2\b': 'second quarter',
            r'\bq3\b': 'third quarter',
            r'\bq4\b': 'fourth quarter',
            r'\b1q\b': 'first quarter',
            r'\b2q\b': 'second quarter',
            r'\b3q\b': 'third quarter',
            r'\b4q\b': 'fourth quarter',
            r'\bfq1\b': 'first fiscal quarter',
            r'\bfq2\b': 'second fiscal quarter',
            r'\bfq3\b': 'third fiscal quarter',
            r'\bfq4\b': 'fourth fiscal quarter',
            r'\bf1q\b': 'first fiscal quarter',
            r'\bf2q\b': 'second fiscal quarter',
            r'\bf3q\b': 'third fiscal quarter',
            r'\bf4q\b': 'fourth fiscal quarter'
        }
        
        for abbrev, full_term in quarter_mappings.items():
            text = re.sub(abbrev, full_term, text, flags=re.IGNORECASE)
        
        # Then handle other abbreviations
        abbreviation_mappings = {
            r'\bfy\b': 'fiscal year',
            r'\byoy\b': 'year-over-year',
            r'\bqoq\b': 'quarter-over-quarter',
            r'\bebitda\b': 'EBITDA',
            r'\bgaap\b': 'GAAP',
            r'\bmrr\b': 'monthly recurring revenue',
            r'\bacv\b': 'annual contract value'
        }
        
        for abbrev, full_term in abbreviation_mappings.items():
            text = re.sub(abbrev, full_term, text, flags=re.IGNORECASE)
        
        # Handle combined patterns (e.g., "fourth quarter fy23")
        text = re.sub(
            r'(\w+)\s+(?:fiscal\s+)?quarter\s+(?:of\s+)?fiscal year\s+(\d{2,4})',
            r'\1 fiscal quarter of fiscal year \'\2',
            text,
            flags=re.IGNORECASE
        )
        
        # Clean up any double spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    @staticmethod
    def normalize_currency(text: str) -> str:
        """Standardize currency formats (e.g., $1M to 1,000,000 dollars)."""
        text = re.sub(r'\$(\d+)K\b', r'\1,000 dollars', text, flags=re.IGNORECASE)
        text = re.sub(r'\$(\d+)M\b', r'\1,000,000 dollars', text, flags=re.IGNORECASE)
        text = re.sub(r'\$(\d+)B\b', r'\1,000,000,000 dollars', text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def remove_table_of_contents(text: str) -> str:
        """Remove table of contents or repetitive dot patterns."""
        text = re.sub(r'\.{2,}', '', text)  # Remove sequences of dots
        text = re.sub(r'\bTable of Contents\b', '', text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def normalize_text(text: str) -> str:
        """Apply all normalization steps to text."""
        text = TranscriptNormalizer.normalize_case(text)
        text = TranscriptNormalizer.normalize_punctuation(text)
        text = TranscriptNormalizer.normalize_numbers(text)
        text = TranscriptNormalizer.normalize_titles(text)
        text = TranscriptNormalizer.normalize_roles(text)
        text = TranscriptNormalizer.normalize_abbreviations(text)
        text = TranscriptNormalizer.normalize_currency(text)
        text = TranscriptNormalizer.remove_table_of_contents(text)
        return text.strip()
    
@step
def normalize_transcript(cleaned_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize the cleaned transcript data."""
    normalized_data = []
    
    for doc in cleaned_data:
        try:
            # Get document components
            content = doc.get("content", {})
            pages = doc.get("pages", [])
            source = doc.get("source", "")
            metadata = doc.get("metadata", {})
            
            # Normalize presentation and Q&A sections
            normalized_content = {
                "presentation": TranscriptNormalizer.normalize_text(content.get("presentation", "")),
                "qa": TranscriptNormalizer.normalize_text(content.get("qa", ""))
            }
            
            # Normalize individual pages
            normalized_pages = []
            for page in pages:
                normalized_pages.append({
                    "page": page.get("page"),
                    "text": TranscriptNormalizer.normalize_text(page.get("text", ""))
                })
            
            # Create normalized document
            normalized_doc = {
                "source": source,
                "content": normalized_content,
                "pages": normalized_pages,
                "metadata": {
                    **metadata,
                    "normalized_length": len(normalized_content["presentation"]) + len(normalized_content["qa"])
                }
            }
            
            logger.info(f"Normalized document {source}: "
                       f"Presentation: {len(normalized_content['presentation'])} chars, "
                       f"Q&A: {len(normalized_content['qa'])} chars, "
                       f"Pages: {len(normalized_pages)}")
            
            normalized_data.append(normalized_doc)
            
        except Exception as e:
            logger.error(f"Error normalizing document {doc.get('source', 'unknown')}: {str(e)}")
            raise
    
    return normalized_data