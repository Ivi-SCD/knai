from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# global modules
from config import global_settings
from router import api_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        log_level='info', 
        reload=True,
        timeout_keep_alive=300,
        limit_max_requests=200,
        limit_concurrency=20
    )