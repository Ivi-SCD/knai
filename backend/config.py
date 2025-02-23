from os import getenv
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import re

load_dotenv()

class GlobalConfig(BaseSettings):
    """
    Global configuration for the application.
    
    Attributes:
        V_STR (str): The version string for the API.
        API_V_STR (str): The versioned API string.
        WATSONX_API_KEY (str): The WatsonX API key.
        ENVIRONMENT (str): The environment the application is running in.
        FRONTEND_URL (str): The URL of the frontend application.
        
        Raises:
        ValueError: If V_STR is not in the format v1.
        VaalueError: If WATSONX_API_KEY is not set.
        
        ods:
        Config: Configuration for the settings.
        
        Returns:
        GlobalConfig: The global configuration.
    """
    V_STR: str = getenv("V_STR",
                        "v1")
    
    if not re.match(r"^v\d+$",
                    V_STR):
        raise ValueError("V_STR must be in the format v1")
    
    ENVIRONMENT: str = getenv("ENVIRONMENT",
                                "DEVELOPMENT")
    
    API_V_STR: str = f"/api/{V_STR}"
    
    LLM_MODEL_ID: str = getenv("LLM_MODEL_ID")
    OLLAMA_MODEL_ID: str = "granite3.1-dense:8b"
    LLM_TEMPERATURE: float = float(getenv("LLM_TEMPERATURE", 0))
    LLM_MAX_TOKENS: int = int(getenv("LLM_MAX_TOKENS", 1280))
    PROJECT_ID: str = getenv("PROJECT_ID",)
    LLM_URL: str = getenv("LLM_URL",)
    if not LLM_URL:
        raise ValueError("LLM_URL must be set")
    if not PROJECT_ID:
        raise ValueError("PROJECT_ID must be set")
    if not LLM_MODEL_ID:
        raise ValueError("LLM_MODEL_ID must be set")
    
    REDIS_URI: str = getenv("REDIS_URI")
    DB_USER: str = getenv("DB_USER", "postgres")
    DB_PASSWORD: str = getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = getenv("DB_HOST", "localhost")
    DB_PORT: int = int(getenv("DB_PORT", 5432))
    DB_NAME: str = getenv("DB_NAME", "postgres")
    
    
    WATSONX_API_KEY: str = getenv('WATSONX_API_KEY')
    
    if not WATSONX_API_KEY:
        raise ValueError("WATSONX_API_KEY must be set")
    
    FRONTEND_URL: str = getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        case_sensitive = True
        
global_settings: GlobalConfig = GlobalConfig()