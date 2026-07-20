from config.mongo_config import COLLECTION_HISTORY
from database.connection import get_db
from database.models import history_doc

def save_history(session_id, **kwargs):
    db = get_db()
    doc = history_doc(session_id=session_id, **kwargs)
    result = db[COLLECTION_HISTORY].insert_one(doc)
    return str(result.inserted_id)

def get_history(session_id, limit=10):
    db = get_db()
    return list(
        db[COLLECTION_HISTORY].find({"session_id": session_id})
        .sort("created_at", -1).limit(limit)
    )
