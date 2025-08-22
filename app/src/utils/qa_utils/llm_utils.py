"""LLM-related utilities for QA service."""
import logging
from typing import List, Dict, Any
from openai import OpenAI

from app.src.utils.qa_utils.client_utils import get_client
from app.src.utils.qa_utils.format_utils import format_json_for_prompt

logger = logging.getLogger(__name__)

async def generate_answer_with_llm(question: str, context: List[Dict[str, Any]]) -> str:
    if not context:
        return "No encuentro información en los documentos cargados."

    try:
        # Tomar el primer documento del contexto
        json_data = context[0].get('content', {})
        
        # Formatear los datos JSON para el prompt
        formatted_data = format_json_for_prompt(json_data)
        
        # Crear el mensaje para el modelo
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente útil que responde preguntas basándose en los datos proporcionados."
            },
            {
                "role": "user",
                "content": f"""Analiza los siguientes datos y responde la pregunta de manera concisa.
                
Datos:
{formatted_data}

Pregunta: {question}

Respuesta:"""
            }
        ]
        
        # Obtener el cliente de OpenAI configurado para Hugging Face
        client = get_client()
        
        # Realizar la petición a la API
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:fireworks-ai",
            messages=messages,
            max_tokens=1000,
            temperature=0.1,
            top_p=0.9
        )
        
        # Extraer y retornar la respuesta
        answer = completion.choices[0].message.content.strip()
        logger.info(f"Respuesta generada para: {question}")
        logger.info(f"Respuesta: {answer}")
        return answer if answer else "No encontré información específica sobre eso en los datos."
        
    except Exception as e:
        logger.error(f"Error al generar respuesta: {str(e)}", exc_info=True)
        return "No pude procesar la solicitud en este momento. Por favor, intenta con otra pregunta."
