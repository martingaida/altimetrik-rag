from qdrant_client import QdrantClient as QClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from loguru import logger
from settings import settings
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class QdrantClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantClient, cls).__new__(cls)
            try:
                # Initialize the Qdrant client with cloud configuration
                cls._instance.client = QClient(
                    url=settings.QDRANT_CLUSTER_URL,
                    api_key=settings.QDRANT_APIKEY,
                )
                logger.info(f"Connected to Qdrant cloud at: {settings.QDRANT_CLUSTER_URL}")
                
                # Initialize collection if it doesn't exist
                cls._instance.init_collection()
                
                # Verify collection exists and has documents
                try:
                    collection_info = cls._instance.client.get_collection(settings.VECTOR_COLLECTION_NAME)
                    points_count = collection_info.points_count
                    logger.info(f"Connected to collection {settings.VECTOR_COLLECTION_NAME} with {points_count} documents")
                except Exception as e:
                    logger.error(f"Error checking collection: {str(e)}")
                
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
        return cls._instance

    def init_collection(self, collection_name: str = settings.VECTOR_COLLECTION_NAME):
        """Initialize collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                logger.info(f"Creating new collection: {collection_name}")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,  # Get dimension from settings
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Successfully created collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def add_documents(self, documents: List[Dict], collection_name: str = settings.VECTOR_COLLECTION_NAME):
        """Add documents to Qdrant collection."""
        try:
            points = []
            for idx, doc in enumerate(documents):
                # Determine if document has precomputed embedding or needs generation
                if 'embedding' in doc and doc['embedding']:
                    vector = doc['embedding']
                else:
                    logger.warning(f"Skipping document {idx} due to missing embedding.")
                    continue
                
                # Metadata extraction
                metadata = {
                    **doc['metadata'],
                    'text': doc['text']
                }
                
                # Create Qdrant PointStruct for each document
                points.append(PointStruct(
                    id=idx,
                    payload=metadata,
                    vector=vector
                ))
            
            if not points:
                logger.warning("No valid documents to add.")
                return
                
            # Upsert points into Qdrant collection
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Successfully added {len(points)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def search_similar(self, query_vector: list[float] = None, query_text: str = None, 
                      collection_name: str = settings.VECTOR_COLLECTION_NAME, 
                      limit: int = 5, filter: Filter = None):
        """Search for similar documents using either a vector or text query."""
        try:
            if query_vector is None and query_text is not None:
                # Generate embedding for the query text using SentenceTransformer
                model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                query_vector = model.encode(query_text).tolist()
            elif query_vector is None and query_text is None:
                raise ValueError("Either query_vector or query_text must be provided")
            
            logger.debug(f"Searching collection {collection_name} with limit {limit}")
            if filter:
                logger.debug(f"Using filter: {filter}")
                
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter
            )
            
            logger.debug(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            return []


connection = QdrantClient()