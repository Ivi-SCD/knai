from config import global_settings
from langchain_ibm import ChatWatsonx

def get_llm_settings():
    """
    Returns the settings for the LLM.
    
    Returns:
        dict: The settings for the LLM.
    """
    params = {
        "temperature": global_settings.LLM_TEMPERATURE,
        "max_tokens":  global_settings.LLM_MAX_TOKENS,
    }
    
    return {
        "model_id": global_settings.LLM_MODEL_ID,
        "project_id": global_settings.PROJECT_ID,
        "url": global_settings.LLM_URL,
        "params" : params,
        "apikey" : global_settings.WATSONX_API_KEY,
    }
    
def get_llm():
     """
     Returns the LLM.
     Returns:
         LLM: The LLM.
     """
     return ChatWatsonx(**get_llm_settings())