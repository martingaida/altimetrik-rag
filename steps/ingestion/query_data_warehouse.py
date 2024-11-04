from typing import List, Dict, Any, Optional
from pymongo import DESCENDING
from settings import settings
from loguru import logger
from zenml import step
import os

from infrastructure.db.mongo import MongoDBClient
from shared.domain.documents import VectorSearchResult


def fetch_all_data(collection) -> List[Dict]:
    """Fetch all documents from MongoDB collection."""
    try:
        documents = list(collection.find({}, {'_id': 1, 'content': 1, 'metadata': 1}))
        logger.info(f"Fetched {len(documents)} documents from MongoDB")
        return documents
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise


def execute_mongo_query(mongo_query: Dict[str, Any], collection_name: str = settings.MONGODB_COLLECTION_NAME, limit: int = None) -> List[VectorSearchResult]:
    """Execute the MongoDB query generated from the IntentDetector."""
    try:
        mongo_client = MongoDBClient(settings.MONGODB_CONNECTION_STRING)
        collection = mongo_client.db.get_collection(collection_name)

        # Parse the query to separate filtering, sorting, and projection
        filter_query = {}
        sort_fields = []
        projection = None

        # Extract special operators from query
        sort_spec = mongo_query.pop('$sort', None)
        limit = mongo_query.pop('$limit', None)
        projection = mongo_query.pop('projection', None)
        
        # Basic find query
        cursor = collection.find(mongo_query, projection)
        
        # Apply sort if specified
        if sort_spec:
            cursor = cursor.sort(list(sort_spec.items()))
            
        # Apply limit if specified
        if limit:
            cursor = cursor.limit(limit)

        # Convert results to VectorSearchResult format
        results = []
        for doc in cursor:
            # Extract metadata fields
            metadata = {}
            if 'metadata' in doc:
                metadata.update(doc['metadata'])
            else:
                # If fields are at top level, include them in metadata
                metadata.update({
                    k: v for k, v in doc.items()
                    if k not in ['_id', 'content', 'metadata']
                })

            result = VectorSearchResult(
                text=f"Database query results: {str(metadata)}",
                metadata=metadata,
                score=1.0
            )
            results.append(result)

        logger.info(f"Found {len(results)} documents matching intent query")
        return results

    except Exception as e:
        logger.error(f"Error executing MongoDB query: {e}", exc_info=True)
        return []
    

@step
def query_data_warehouse(collections: List[str]) -> List[Dict]:
    """Query MongoDB for documents."""
    all_documents = []
    mongo_client = MongoDBClient(settings.MONGODB_CONNECTION_STRING)
    
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
