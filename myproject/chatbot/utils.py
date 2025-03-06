import re
import magic
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}
mime_checker = magic.Magic(mime=True)

def allowed_file(filename, file_stream):
    allowed_ext = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    file_type = mime_checker.from_buffer(file_stream.read(1024))
    file_stream.seek(0)
    return allowed_ext and file_type.startswith(('image/', 'audio/', 'video/'))

def is_password_complex(password):
    return (len(password) >= 8 and 
            re.search(r"\d", password) and 
            re.search(r"[A-Z]", password) and 
            re.search(r"[a-z]", password))