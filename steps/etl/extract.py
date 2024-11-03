from typing import List, Dict, Any
from zenml import step
from steps.etl.download import download_zip

@step
def extract_data(
    zip_url: str,
) -> List[Dict[str, Any]]:
    """Extract digital data from zip file."""
    # Download and extract documents from zip file
    documents = download_zip(zip_url=zip_url)
    return documents