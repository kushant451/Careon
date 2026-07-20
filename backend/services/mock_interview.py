from database import interview_collection

def start_session(session_id, role, questions, personalized=False):
    return interview_collection.create_interview(session_id, role, questions, personalized)

def get_session(session_id):
    return interview_collection.get_interview(session_id)

def record_answer(session_id, index, answer, evaluation):
    interview_collection.save_answer(session_id, index, answer, evaluation)

def advance(session_id, next_index):
    interview_collection.advance_question(session_id, next_index)

def end_session(session_id):
    interview_collection.complete_interview(session_id)