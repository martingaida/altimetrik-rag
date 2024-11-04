from zenml import pipeline
from steps.ingestion.query_data_warehouse import query_data_warehouse
from steps.ingestion.clean import clean_documents
from steps.ingestion.chunk_embed import chunk_and_embed
from steps.ingestion.load_to_vector_db import load_to_vector_db
from settings import settings

@pipeline(enable_cache=False)
def data_ingestion_pipeline():
    """Pipeline for ingesting documents into the vector store."""
    # Query data using collections from settings
    documents = query_data_warehouse(collections=[settings.MONGODB_COLLECTION_NAME])
    
    # Clean documents
    cleaned_documents = clean_documents(documents=documents)
    
    # Chunk and embed
    embedded_chunks = chunk_and_embed(documents=cleaned_documents)
    
    # Save embedded chunks
    load_to_vector_db(documents=embedded_chunks)