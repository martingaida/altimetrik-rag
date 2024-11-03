import re
from typing import List


def clean_text(text: str) -> str:
    """Clean text by removing unwanted patterns and normalizing whitespace."""
    if not text:
        return ""
        
    # Remove special characters and normalize whitespace
    text = re.sub(r'[\r\n\t]+', ' ', text)  # Replace newlines and tabs with space
    text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces
    text = text.strip()
    
    return text
