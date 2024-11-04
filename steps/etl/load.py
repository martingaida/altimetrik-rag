from infrastructure.db.mongo import MongoDBClient
from typing import List, Dict
from datetime import datetime
from zenml import step
from loguru import logger

@step
def load_data(
    documents: List[Dict],
    collection_name: str,
    mongodb_connection_string: str
) -> str:
    """Store documents in MongoDB."""
    # Initialize MongoDB client with provided connection string
    mongo_client = MongoDBClient(mongodb_connection_string)
    collection = mongo_client.db.get_collection(collection_name)
    
    # Add metadata to documents
    timestamp = datetime.utcnow()
    processed_docs = []
    
    for doc in documents:
        processed_doc = {
            "content": doc.get("content", ""),
            "metadata": {
                **doc.get("metadata", {}),
                "ingestion_timestamp": timestamp,
                "last_updated": timestamp,
            }
        }
        processed_docs.append(processed_doc)
    
    try:
        # First, clear existing documents (optional)
        collection.delete_many({})
        logger.info(f"Cleared existing documents from {collection_name}")
        
        # Insert documents
        if processed_docs:
            result = collection.insert_many(processed_docs)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents into {collection_name}")
            
            # Verify insertion
            count = collection.count_documents({})
            logger.info(f"Total documents in collection after insertion: {count}")
            
            return f"Inserted {len(result.inserted_ids)} documents"
        else:
            logger.warning("No documents to insert")
            return "No documents to insert"
            
    except Exception as e:
        logger.error(f"Failed to insert documents: {e}")
        raise