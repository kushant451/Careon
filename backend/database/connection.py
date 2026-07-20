from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.settings import MONGO_URI, MONGO_DB_NAME
from utils.logger import get_logger

logger = get_logger(__name__)
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
            _client.admin.command("ping")
            _db = _client[MONGO_DB_NAME]
            logger.info("MongoDB connected → %s", MONGO_DB_NAME)
        except ConnectionFailure as exc:
            raise RuntimeError(
                "Cannot connect to MongoDB. "
                "Make sure MongoDB is running and MONGO_URI in .env is correct."
            ) from exc
    return _db

def close_db():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None