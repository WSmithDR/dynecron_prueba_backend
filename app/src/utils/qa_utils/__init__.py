"""
QA Utility Module

This package contains utility functions for the QA Service.
"""

from app.src.utils.qa_utils.client_utils import get_client
from app.src.utils.qa_utils.document_utils import check_documents_exist
from app.src.utils.qa_utils.format_utils import format_json_for_prompt, format_sources
from app.src.utils.qa_utils.llm_utils import generate_answer_with_llm
from app.src.utils.qa_utils.citation_utils import create_citations

__all__ = [
    'get_client',
    'check_documents_exist',
    'format_json_for_prompt',
    'format_sources',
    'generate_answer_with_llm',
    'create_citations'
]
