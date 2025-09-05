
ALLOWED_EXTENSIONS = {"pdf", "txt"}

def is_extension_allowed(filename: str) -> bool:
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    