from ..utils.text_utils import clean_text, split_into_chunks
from typing import List

def process_content(content: str) -> List[str]:
    """Process content into clean, meaningful chunks."""
    cleaned = clean_text(content).lower()
    return split_into_chunks(cleaned)