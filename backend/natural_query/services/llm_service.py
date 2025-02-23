from langchain_ollama import OllamaLLM
from langchain_ibm import ChatWatsonx
from config import global_settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service to manage LLM's interactions
    """
    @staticmethod
    def getwatson_llm():

        parameters = {
            "temperature": global_settings.LLM_TEMPERATURE
        }

        chat = ChatWatsonx(
            model_id=global_settings.LLM_MODEL_ID,
            params=parameters,
            url=global_settings.LLM_URL,
            project_id=global_settings.PROJECT_ID,
            apikey=global_settings.WATSONX_API_KEY
        )

        return chat
    
    @staticmethod
    def get_llm():
        llm = OllamaLLM(
            model=global_settings.OLLAMA_MODEL_ID, 
            temperature=global_settings.LLM_TEMPERATURE,
        )
        return llm

llmService: LLMService = LLMService()