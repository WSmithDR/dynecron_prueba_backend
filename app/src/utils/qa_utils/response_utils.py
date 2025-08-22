"""Response cleaning and formatting utilities for QA service."""
import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def clean_response(response: str) -> str:
    """
    Clean the response by removing any keyword markers and extra whitespace.
    
    Args:
        response: The raw response string that might contain keyword markers
        
    Returns:
        str: Cleaned response with keyword markers removed
    """
    if not response:
        return ""
    
    # Remove keyword markers and surrounding whitespace
    clean_response = re.sub(r'\s*\[\[.*?\]\]\s*', '', response).strip()
    return clean_response if clean_response else response
