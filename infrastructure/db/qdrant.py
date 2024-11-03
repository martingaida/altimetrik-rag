from qdrant_client import QdrantClient as QClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from loguru import logger
from settings import settings
from typing import List, Dict


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
                    # Generate embedding if not provided
                    text = doc.get('text') or doc.get('content', '')
                    vector = self._generate_embedding(text)
                
                if not vector:
                    logger.warning(f"Skipping document {idx} due to missing embedding.")
                    continue
                
                # Metadata extraction
                metadata = {
                    'category': doc['metadata']['category'],
                    'chunk_index': doc['metadata']['chunk_index'],
                    'original_id': doc['metadata']['original_id'],
                    'start_char': doc['metadata']['start_char'],
                    'end_char': doc['metadata']['end_char'],
                    'text': doc['text'][:200]
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

    def search_similar(self, query_text: str, collection_name: str = settings.VECTOR_COLLECTION_NAME, limit: int = 5):
        """Search for similar documents."""
        try:
            # Generate embedding for the query text
            query_vector = self._generate_embedding(query_text)
            if not query_vector:
                logger.error("Failed to generate embedding for query text.")
                return []
            
            results = self.client.search(
                collection_name=collection_name,
                vector=query_vector,
                limit=limit
            )
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise


connection = QdrantClient()