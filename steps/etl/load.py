from typing import List, Dict, Any
from zenml import step
from pymongo import MongoClient
from loguru import logger
from datetime import datetime

@step
def load_data(
    documents: List[Dict[str, Any]],
    collection_name: str,
    mongodb_connection_string: str,
) -> str:
    """Store documents in MongoDB."""
    client = MongoClient(mongodb_connection_string)
    db = client.get_database("digital_data")
    collection = db.get_collection(collection_name)
    
    # Add metadata to documents
    for doc in documents:
        doc["_imported_at"] = datetime.utcnow()
    
    # Insert documents
    if documents:
        result = collection.insert_many(documents)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into MongoDB")
        inserted_count = len(result.inserted_ids)
    else:
        inserted_count = 0
    
    client.close()
    return f"Inserted {inserted_count} documents into MongoDB"