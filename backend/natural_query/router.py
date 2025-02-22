from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from .service import KNAIService

router = APIRouter()
knai_service = KNAIService()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    response: Dict[str, Any]

@router.post('/', response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query and return the results
    """
    try:
        result = await knai_service.process_query(request.query)
        return result
    except Exception as e:
        raise QueryResponse(
            status="error",
            response={
                "message": str(e)
            }
        )