from typing import Optional
from loguru import logger
from pymongo import MongoClient
from settings import settings


class MongoDBClient:
    _instance: Optional['MongoDBClient'] = None
    _client: Optional[MongoClient] = None
    _db = None

    def __new__(cls, connection_string: Optional[str] = None) -> 'MongoDBClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                uri = connection_string or settings.MONGODB_CONNECTION_STRING
                cls._instance._client = MongoClient(uri)
                cls._instance._db = cls._instance._client[settings.MONGODB_DATABASE_NAME]
                logger.info(f"Connected to MongoDB database: {settings.MONGODB_DATABASE_NAME}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return cls._instance

    @property
    def db(self):
        return self._db

    @property
    def client(self):
        return self._client


# Initialize without connection string - will use settings
mongodb = MongoDBClient()
database = mongodb.db
