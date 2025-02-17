import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# global modules
from config import global_settings
from router import api_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[global_settings.FRONTEND_URL],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

app.include_router(api_router,
                   prefix=global_settings.API_V_STR)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("main:app",
                log_level='info', reload=True)