from typing import Optional
from zenml import pipeline
from steps.etl.extract import extract_data
from steps.etl.clean import clean_transcript
from steps.etl.normalize import normalize_transcript
from steps.etl.transform import transform_transcript
from steps.etl.load import load_data

@pipeline(enable_cache=True)
def data_etl_pipeline(
    zip_url: str,
    collection_name: str,
    mongodb_connection_string: str
) -> None:
    """Pipeline to download zip file, extract contents, transform, and store in MongoDB."""
    # Extract data from zip file
    raw_documents = extract_data(zip_url=zip_url)
    
    # Clean the documents
    cleaned_documents = clean_transcript(raw_data=raw_documents)
    
    # Normalize the documents
    normalized_documents = normalize_transcript(cleaned_data=cleaned_documents)
    
    # Transform the documents
    transformed_documents = transform_transcript(raw_data=normalized_documents)
    
    # Store in MongoDB
    load_data(
        documents=transformed_documents,
        collection_name=collection_name,
        mongodb_connection_string=mongodb_connection_string
    )