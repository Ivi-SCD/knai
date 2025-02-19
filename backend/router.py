from fastapi import APIRouter

from natural_query.router import router as natural_query_router

api_router = APIRouter()

api_router.include_router(natural_query_router,
                          prefix="/natural_query")

@api_router.get("/health_check")
async def get_health_check():
    return "Server is running"