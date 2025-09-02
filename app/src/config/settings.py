from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent.parent

# Directory where uploaded files will be stored
UPLOAD_DIR = BASE_DIR.parent / "data"  # Changed to point to the project root/data

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Search service configuration
SEARCH_CONFIG = {
    "min_confidence": 0.3,  # Minimum confidence score for search results
    "page_size": 10,        # Default number of results per page
    "max_results": 1000,    # Maximum number of results to return
}

# API configuration
API_CONFIG = {
    "title": "Document QA API",
    "description": "API for document question answering",
    "version": "1.0.0",
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
