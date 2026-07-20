import os, uuid
from werkzeug.utils import secure_filename
from config.settings import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, session_id):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    unique_name = f"{session_id}_{uuid.uuid4().hex[:8]}_{filename}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)
    return save_path, filename