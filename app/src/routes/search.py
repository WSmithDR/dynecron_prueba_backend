from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from ..services.search_service import search_service

router = APIRouter()

@router.get("/search")
async def search(q: str, limit: int = 5):
    try:
        return search_service.search(q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
