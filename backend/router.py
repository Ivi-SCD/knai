from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health_check")
async def get_health_check():
    return "Server is running"