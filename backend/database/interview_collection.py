from datetime import datetime
from config.mongo_config import COLLECTION_INTERVIEWS
from database.connection import get_db
from database.models import interview_doc

def create_interview(session_id, role, questions, personalized=False):
    db = get_db()
    db[COLLECTION_INTERVIEWS].delete_many({"session_id": session_id, "status": "in_progress"})
    doc = interview_doc(session_id, role, questions, personalized)
    result = db[COLLECTION_INTERVIEWS].insert_one(doc)
    return str(result.inserted_id)

def get_interview(session_id):
    db = get_db()
    return db[COLLECTION_INTERVIEWS].find_one(
        {"session_id": session_id, "status": "in_progress"},
        sort=[("started_at", -1)]
    )

def save_answer(session_id, index, answer, evaluation):
    db = get_db()
    db[COLLECTION_INTERVIEWS].update_one(
        {"session_id": session_id, "status": "in_progress"},
        {"$set": {f"answers.{index}": answer, f"evaluations.{index}": evaluation}},
        sort=[("started_at", -1)]
    )

def advance_question(session_id, next_index):
    db = get_db()
    db[COLLECTION_INTERVIEWS].update_one(
        {"session_id": session_id, "status": "in_progress"},
        {"$set": {"current_index": next_index}},
        sort=[("started_at", -1)]
    )

def complete_interview(session_id):
    db = get_db()
    db[COLLECTION_INTERVIEWS].update_one(
        {"session_id": session_id, "status": "in_progress"},
        {"$set": {"status": "completed", "completed_at": datetime.utcnow()}},
        sort=[("started_at", -1)]
    )