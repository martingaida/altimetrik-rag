from typing import List, Dict
from zenml import step
from infrastructure.db.mongo import MongoDBClient
from loguru import logger
import os

def fetch_all_data(collection) -> List[Dict]:
    """Fetch all documents from MongoDB collection."""
    try:
        documents = list(collection.find({}, {'_id': 1, 'content': 1, 'metadata': 1}))
        logger.info(f"Fetched {len(documents)} documents from MongoDB")
        return documents
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise

@step
def query_data_warehouse(collections: List[str]) -> List[Dict]:
    """Query MongoDB for documents."""
    all_documents = []
    mongo_client = MongoDBClient(os.getenv("MONGODB_CONNECTION_STRING"))
    
    for collection_name in collections:
        logger.info(f"Querying data warehouse for collection: {collection_name}")
        collection = mongo_client.db.get_collection(collection_name)
        
        # Fetch documents
        documents = fetch_all_data(collection)
        logger.info(f"Found {len(documents)} documents in collection {collection_name}")
        
        # Add collection metadata
        for doc in documents:
            doc["metadata"]["collection_name"] = collection_name
            doc["metadata"]["collection_total_docs"] = str(len(documents))
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            all_documents.append(doc)
    
    logger.info(f"Total documents processed: {len(all_documents)}")
    
    # Log sample document structure if available
    if all_documents:
        logger.debug(f"Sample document structure: {all_documents[0].keys()}")
    
    return all_documents
