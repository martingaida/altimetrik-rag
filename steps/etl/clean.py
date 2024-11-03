from typing import List, Dict, Any
from zenml import step
from loguru import logger
import re

class TranscriptCleaner:
    @staticmethod
    def remove_timestamps(text: str) -> str:
        """Remove various timestamp formats from text."""
        text = re.sub(r'\[\d{1,2}:\d{2}(:\d{2})?\]', '', text)  # [00:02:15]
        text = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\s?(AM|PM|am|pm)?\b', '', text)  # 0:02:15 PM
        text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text)  # 00:02
        return text

    @staticmethod
    def remove_metadata(text: str) -> str:
        """Remove headers, footers, disclaimers, and other metadata."""
        patterns = [
            r'(Refinitiv|Disclaimer|Confidential):.*?\n',
            r'Page \d+ of \d+',
            r'Copyright © \d{4}.*?\n',
            r'All rights reserved.*?\n',
            r'\(technical difficulty\)',
            r'(?i)operator instructions',
            r'\.{3,}',  # Sequences of dots for table of contents
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        return text.strip()

    @staticmethod
    def split_sections(text: str) -> Dict[str, str]:
        """Split transcript into presentation and Q&A sections."""
        qa_markers = [
            r'\bQ&A\b',
            r'\bQuestions and Answers\b',
            r'\bQuestion-and-Answer Session\b'
        ]
        
        presentation_markers = [
            r'\bPresentation\b',
            r'\bPrepared Remarks\b',
            r'\bOpening Remarks\b'
        ]
        
        qa_text, presentation_text = "", text
        for marker in qa_markers:
            if re.search(marker, text, re.IGNORECASE):
                parts = re.split(marker, text, flags=re.IGNORECASE)
                presentation_text, qa_text = parts[0].strip(), parts[1].strip()
                break
        
        # Remove presentation section markers
        for marker in presentation_markers:
            presentation_text = re.sub(marker, '', presentation_text, flags=re.IGNORECASE)
        
        return {
            "presentation": presentation_text.strip(),
            "qa": qa_text.strip()
        }

    @staticmethod
    def clean_filler_words(text: str) -> str:
        """Remove filler words and standardize punctuation."""
        fillers = [
            r'\b(um|uh|er|ah|like)\b',
            r'\byou know\b',
            r'\bI mean\b',
            r'\bso\b',
            r'\bbasically\b',
            r'\bactually\b',
            r'\bkind of\b',
            r'\bsort of\b',
            r'\bright\b',
            r'\bokay\b'
        ]
        for filler in fillers:
            text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace and punctuation
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\s*([.,?!:;])\s*', r'\1 ', text)  # Standardize punctuation spacing
        text = re.sub(r'([.,?!:;]){2,}', r'\1', text)  # Remove multiple punctuation
        
        return text.strip()
    
    @staticmethod
    def remove_special_characters(text: str) -> str:
        """Remove or standardize unnecessary special characters in the text."""
        # Remove caret symbols, asterisks, and other unnecessary symbols
        text = re.sub(r'[\^*#]', '', text)

        # Remove empty parentheses and content-less tags, e.g., ( )
        text = re.sub(r'\(\s*\)', '', text)
        
        # Remove unnecessary technical indicators like (technical difficulty)
        text = re.sub(r'\((technical difficulty|laughter|applause|audio unavailable)\)', '', text, flags=re.IGNORECASE)
        
        # Remove standalone parentheses and brackets often used for notes
        text = re.sub(r'[\[\](){}]', '', text)

        return text.strip()

    @staticmethod
    def clean_transcript(text: str) -> Dict[str, Any]:
        """Apply all cleaning steps to transcript text."""
        text = TranscriptCleaner.remove_timestamps(text)
        text = TranscriptCleaner.remove_metadata(text)
        text = TranscriptCleaner.clean_filler_words(text)
        text = TranscriptCleaner.remove_special_characters(text)
        sections = TranscriptCleaner.split_sections(text)
        
        return sections

@step
def clean_transcript(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and normalize the raw digital data."""
    cleaned_data = []
    
    for doc in raw_data:
        try:
            content = doc.get("content", "")
            source = doc.get("source", "")
            pages = doc.get("pages", [])
            metadata = doc.get("metadata", {})
            
            if not content.strip():
                logger.warning(f"Skipping empty document: {source}")
                continue
            
            cleaned_sections = TranscriptCleaner.clean_transcript(content)
            cleaned_pages = [
                {
                    "page": page.get("page"),
                    "text": TranscriptCleaner.clean_filler_words(
                        TranscriptCleaner.remove_metadata(
                            TranscriptCleaner.remove_timestamps(page.get("text", ""))
                        )
                    )
                } for page in pages
            ]
            
            cleaned_doc = {
                "source": source,
                "content": cleaned_sections,
                "pages": cleaned_pages,
                "metadata": {
                    **metadata,
                    "original_length": len(content),
                    "cleaned_length": len(cleaned_sections["presentation"]) + len(cleaned_sections["qa"]),
                    "page_count": len(cleaned_pages)
                }
            }
            
            logger.info(f"Cleaned document {source}: "
                        f"Presentation: {len(cleaned_sections['presentation'])} chars, "
                        f"Q&A: {len(cleaned_sections['qa'])} chars, "
                        f"Pages: {len(cleaned_pages)}")
            
            cleaned_data.append(cleaned_doc)
        except Exception as e:
            logger.error(f"Failed to clean document {source}: {e}")
            continue
    
    return cleaned_data