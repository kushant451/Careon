from config.mongo_config import (
    COLLECTION_CAREER_RECS, COLLECTION_ROADMAPS, COLLECTION_JOB_MATCHES,
)
from database.connection import get_db
from database.models import career_recommendation_doc, roadmap_doc, job_match_doc


def save_career_recommendation(session_id, **kwargs):
    db = get_db()
    doc = career_recommendation_doc(session_id=session_id, **kwargs)
    db[COLLECTION_CAREER_RECS].delete_many({"session_id": session_id})
    result = db[COLLECTION_CAREER_RECS].insert_one(doc)
    return str(result.inserted_id)

def get_career_recommendation(session_id):
    db = get_db()
    return db[COLLECTION_CAREER_RECS].find_one(
        {"session_id": session_id}, sort=[("created_at", -1)]
    )

def save_roadmap(session_id, **kwargs):
    db = get_db()
    doc = roadmap_doc(session_id=session_id, **kwargs)
    db[COLLECTION_ROADMAPS].delete_many({"session_id": session_id})
    result = db[COLLECTION_ROADMAPS].insert_one(doc)
    return str(result.inserted_id)

def get_roadmap(session_id):
    db = get_db()
    return db[COLLECTION_ROADMAPS].find_one(
        {"session_id": session_id}, sort=[("created_at", -1)]
    )


def save_job_match(session_id, **kwargs):
    db = get_db()
    doc = job_match_doc(session_id=session_id, **kwargs)
    result = db[COLLECTION_JOB_MATCHES].insert_one(doc)
    return str(result.inserted_id)

def get_job_matches(session_id, limit=10):
    db = get_db()
    return list(
        db[COLLECTION_JOB_MATCHES].find({"session_id": session_id})
        .sort("created_at", -1).limit(limit)
    )