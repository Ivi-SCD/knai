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
    
    WATSONX_API_KEY: str = getenv('WATSONX_API_KEY')
    
    if not WATSONX_API_KEY:
        raise ValueError("WATSONX_API_KEY must be set")
    
    FRONTEND_URL: str = getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        case_sensitive = True
        
global_settings: GlobalConfig = GlobalConfig()