from config.mongo_config import COLLECTION_RESUMES
from database.connection import get_db
from database.models import resume_doc

def save_resume(session_id, **kwargs):
    db = get_db()
    doc = resume_doc(session_id=session_id, **kwargs)
    result = db[COLLECTION_RESUMES].insert_one(doc)
    return str(result.inserted_id)

def get_resume(session_id):
    db = get_db()
    return db[COLLECTION_RESUMES].find_one(
        {"session_id": session_id}, sort=[("created_at", -1)]
    )

def delete_resume(session_id):
    db = get_db()
    db[COLLECTION_RESUMES].delete_many({"session_id": session_id})