"""Keyword extraction utilities for QA service."""
import re
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from a text that contains keyword markers.
    
    Args:
        text: Text that might contain keyword markers [[keyword1, keyword2, ...]]
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    keyword_match = re.search(r'\[\[(.*?)\]\]', text)
    if not keyword_match:
        return []
        
    keyword_str = keyword_match.group(1)
    return [kw.strip() for kw in keyword_str.split(',') if kw.strip()]
