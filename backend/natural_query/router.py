from fastapi import APIRouter, HTTPException
from config import global_settings
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .service import ConversationManager, KNAIService

router = APIRouter()

conversation_manager = ConversationManager(redis_url=global_settings.REDIS_URI)
knai_service = KNAIService(conversation_manager)

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    status: str
    response: Dict[str, Any]

@router.post('/', response_model=QueryResponse)
def process_query(request: QueryRequest):
    """Process a natural language query and return the results"""
    try:
        result = knai_service.process_query(
            request.query,
            conversation_id=request.conversation_id
        )
        return result
    except Exception as e:
        return QueryResponse(
            status="error",
            response={
                "message": str(e)
            }
        )