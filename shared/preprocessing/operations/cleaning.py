import re
from typing import List
from datetime import datetime


def clean_text(text: str) -> str:
    """Clean text by removing unwanted patterns and normalizing whitespace."""
    if not text:
        return ""
        
    # Remove special characters and normalize whitespace
    text = re.sub(r'[\r\n\t]+', ' ', text)  # Replace newlines and tabs with space
    text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces
    text = text.strip()
    
    return text

def parse_pdf_date(date_str):
    """Parse PDF date string format into ISO 8601 timestamp string."""
    if not date_str or not date_str.startswith('D:'):
        return None
    
    # Remove 'D:' prefix and include seconds
    date_str = date_str[2:16]  # Take YYYYMMDDHHmmSS
    
    try:
        dt = datetime.strptime(date_str, '%Y%m%d%H%M%S')
        return dt.strftime('%Y-%m-%dT%H:%M:%S')  # ISO 8601 format
    except ValueError:
        return None
