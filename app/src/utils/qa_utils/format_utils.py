"""Formatting utilities for QA service."""
from typing import Any, List

def format_json_for_prompt(data: Any, indent: int = 0) -> str:
    """Formatea datos JSON para mostrarlos en el prompt."""
    if isinstance(data, dict):
        return '\n'.join([
            f"{'  ' * indent}{key} ({type(value).__name__}): {format_json_for_prompt(value, indent + 1)}"
            for key, value in data.items()
        ])
    elif isinstance(data, list):
        return '\n'.join([
            f"{'  ' * indent}- {format_json_for_prompt(item, indent + 1)}"
            for item in data
        ])
    else:
        return str(data)

def format_sources(sources: List[str]) -> str:
    """Formatea la información de fuentes para la respuesta."""
    if not sources:
        return ""
    return "\n\nFuentes:\n" + "\n".join(f"- {source}" for source in sources)
