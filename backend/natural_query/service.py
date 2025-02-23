from .tools import sql_generator, execute_query
from .services.llm_service import llmService
from dataclasses import dataclass, field
from config import global_settings
from typing import Dict, List, Optional
from datetime import datetime
import logging
import uuid
import redis
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
@dataclass
class Message:
    role: str
    content: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

class ConversationManager:
    
    def __init__(self, redis_url: str = global_settings.REDIS_URI):
        """
        Initialize the manager converse
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            self.redis_client = redis.from_url(redis_url)
            self.conversation_ttl = 24 * 60 * 60  # 24 horas em segundos
        except redis.RedisError as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            raise

    def create_conversation(self) -> str:
        """
        Create a new conversation
        
        Returns:
            str: Unic ID
        """
        conversation_id = str(uuid.uuid4())
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Add a message to conversational historic
        
        Args:
            conversation_id: Conversation ID
            role: Role emissor ('user' ou 'assistant')
            content: Message Content
        """
        try:
            message = Message(role=role, content=content)
            
            history = self.get_conversation_history(conversation_id) or []
            
            history.append(message.__dict__)
            
            self.redis_client.setex(
                f"conv:{conversation_id}",
                self.conversation_ttl,
                json.dumps(history)
            )
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {e}")
            raise

    def get_conversation_history(self, conversation_id: str, 
                               last_n: Optional[int] = None) -> List[Dict]:
        """
        Recover the conversation history
        
        Args:
            conversation_id: Conversation ID
            last_n: Optional parameter
            
        Returns:
            List of historical messages
        """
        try:
            history_json = self.redis_client.get(f"conv:{conversation_id}")
            
            if not history_json:
                return []
                
            history = json.loads(history_json)
            
            if last_n:
                return history[-last_n:]
            return history
        except Exception as e:
            logger.error(f"Error retrieving conversation history for {conversation_id}: {e}")
            return []

class KNAIService:
    """
    A service class for processing natural language queries and generating insights or SQL queries.
    """
    
    def __init__(self, conversation_manager: ConversationManager):
        """
        Initializes the KNAIService instance, setting up the LLM instance and query history.
        """
        self.instance_llm = llmService.getwatson_llm()
        self.conversation_manager = conversation_manager


    def _verify_question(self, question: str) -> str:
        """
        Verifies whether a query is a data request or a casual interaction.

        Args:
            question: A natural language query from the user.

        Returns:
            A string indicating whether the query is a "sql_request" or "casual_interaction".
        """
        try:
            request_verification = f"""
                <|system|>
                    You are an assistant specialized in determining whether a query is a data request or a casual interaction with the user. Your task is to analyze the query and return one of the following fixed responses to classify the query:
                    If the query is a data request (e.g., "What's the most expensive product?", "How many sales did we have today?", etc.), return: "sql_request"
                    If the query is a casual interaction, such as a greeting or thank you (e.g., "hi", "thanks", "good afternoon", etc.), return: "casual_interaction"

                    Important: Only return "sql_request" or "casual_interaction" and nothing else. Do not provide explanations or additional context. Simply classify the query according to the examples above.

                <|user|> 
                    {question}

                <|assistant|>
            """

            response = self.instance_llm.invoke(request_verification).content
            return response.strip()
        except Exception as e:
            logger.error(f"Error verifying question type: {e}")
            raise


    def _answer_question_knai(self, context_messages: List[str], question: str) -> str:
        """
        Generates a response to a user query based on the provided context using LLM.

        Args:
            context_messages: A list of previous context messages to guide the response.
            question: The user's natural language question.

        Returns:
            A friendly, conversational answer based on the context.
        """
        try:
            context = "\n".join(context_messages[-10:])

            prompt = f"""
                <|context|>
                    {context}

                <|user|> 
                    {question}

                <|role|>
                    Your main function is to answer about product, sales and extract insight of data. 
                    We are a enterprise with AI Engineers, Designers and Developers that are together
                    to delivery critical resources to solve business problems with Generative AI and innovative tools
                    We born in 2025 with main idea to solve business problemas with IBM resources
                    
                <|system|>
                    Your name is KNAI Assistant, if is your first message with the user, try to explain about your COMPANY,
                    you work for this guys:
                        - Ivisson is the AI Developer, kindness guy :)
                        - Giu is an AI Engineer, big engineer building a solid career
                        - Marcos is our amazing frontender
                        - Dani is our AI Researcher that drive the business model
                        - Xoto (Hugo) is the designer tha created our visual identity
                        - Edson is our AI Engineer.
                    Respond in a friendly, conversational tone to the user query based on the provided context.
                
                <|assistant|>
            """

            final_answer = self.instance_llm.invoke(prompt)
            return final_answer.content
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
        
    def process_query(self, natural_query: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Processes a user query
        
        Args:
            natural_query: Natural language query
            conversation_id: Optional conversation ID. If not provided, creates a new one.
            
        Returns:
            Dict with processed response
        """
        try:
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation()
                
            logger.info(f"Processing query for conversation {conversation_id}")
            
            # Verify query type
            query_type = self._verify_question(natural_query)
            
            if query_type == 'casual_interaction':
                history = self.conversation_manager.get_conversation_history(
                    conversation_id, 
                    last_n=10
                )
                history_formatted = [
                    f"<{msg['role']}> {msg['content']}" 
                    for msg in history
                ]
                
                model_response = self._answer_question_knai(
                    history_formatted, 
                    natural_query
                )
                
                # Add interaction to history
                self.conversation_manager.add_message(
                    conversation_id, 
                    "user", 
                    natural_query
                )
                self.conversation_manager.add_message(
                    conversation_id, 
                    "assistant", 
                    model_response
                )
                
                response = {
                    "final_answer": model_response,
                    "sql_query": None,
                    "query_result": None,
                    "conversation_id": conversation_id
                }
                
                return {
                    "status": "success",
                    "response": response
                }
            
            # SQL query processing
            sql_query = sql_generator(natural_query)
            logger.info(f"Generated SQL query: {sql_query}")
            
            if sql_query == "NO_CONTEXT":
                return {
                    "status": "error",
                    "response": {
                        "message": "Failed to generate a valid SQL query"
                    }
                }
                
            query_result = execute_query(sql_query)
            logger.info(f"Query result: {query_result}")
            
            context = f"""<user query> {sql_query} 
                        <result query> {query_result}"""
            
            prompt = f"""
                <|context|>
                    {context}

                <|system|>
                    You received a JSON result with a question and an answer. You are an expert data analyst
                    with extensive experience in extracting insight and providing strategic recommendations. 
                    Your main task is to analyze the provided data comprehensively and generate actionable insights in a human-friendly response.
                    Use the query result to explain any key patterns, trends, and insights that can be derived from the data.
        
                <|example|>
                    <user> What are the main factors driving the drop in our Sales Revenue this week?
                    <result query> sales_revenue\tpercentage_down\tsales_date_time\n9.7M\t4%\t2025-22-02\n11M\t12%\t2025-18-02
                    <assistant> 
                     Sales revenue has decreased by 4%, with a total of 9.7M in revenue this week, down from 11M the previous week (a decrease of 1.3M). Key contributing factors include:
            
                        1. A 12% drop in sales revenue from 11M to 9.7M over the past week, signaling a decline in overall sales performance.
                        2. A reduction in user engagement, particularly from paid ads. The number of users driven by paid ads decreased by 17%, from 250k to 147k, leading to a loss of 138k in revenue.
                        
                        Recommendations:
                        - Investigate the effectiveness of your paid ad campaigns and consider optimizing targeting to regain lost users.
                        - Analyze customer behavior and purchase patterns to identify other potential causes of the decline.
                        - Reevaluate pricing or promotional strategies to stimulate sales and increase revenue.
                        - Consider alternative marketing strategies to diversify your revenue streams.
                        
                        In conclusion, the drop in sales revenue seems to be linked to both a decrease in user acquisition through paid ads and broader sales performance trends. Adjusting your marketing and sales strategies could help mitigate the decline.
                <|end_example|>

                <|assistant|>
            """
            
            final_answer = self.instance_llm.invoke(prompt)
            
            # Add interaction to history
            self.conversation_manager.add_message(
                conversation_id, 
                "user", 
                natural_query
            )
            self.conversation_manager.add_message(
                conversation_id, 
                "assistant", 
                final_answer.content
            )
            
            response = {
                "final_answer": final_answer.content,
                "sql_query": sql_query,
                "query_result": query_result,
                "conversation_id": conversation_id
            }
            
            return {
                "status": "success",
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "response": {
                    "message": f"Error processing query: {str(e)}"
                }
            }