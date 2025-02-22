from .tools import sql_generator, execute_query
from .services.llm_service import llmService
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
class KNAIService():
    """
    A service class for processing natural language queries and generating insights or SQL queries.
    """
    
    def __init__(self):
        """
        Initializes the KNAIService instance, setting up the LLM instance and query history.
        """

        self.instance_llm = llmService.getwatson_llm()
        self.history = []


    def _verify_question(self, question: str) -> str:
        """
        Verifies whether a query is a data request or a casual interaction.

        Args:
            question: A natural language query from the user.

        Returns:
            A string indicating whether the query is a "sql_request" or "casual_interaction".
        """

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

        return self.instance_llm.invoke(request_verification).content


    def _answer_question_knai(self, context_messages: List[str], question: str) -> str:
        """
        Generates a response to a user query based on the provided context using LLM.

        Args:
            context_messages: A list of previous context messages to guide the response.
            question: The user's natural language question.

        Returns:
            A friendly, conversational answer based on the context.
        """

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
        """ # Here is a easter egg

        final_answer = self.instance_llm.invoke(prompt)

        self.history.append(f"<user> {question}")
        self.history.append(f"<assistant> {final_answer.content}")

        return final_answer.content

    def process_query(self, natural_query: str) -> Dict:
        """
        Processes the user query by verifying its type and generating the appropriate response, either through natural language or SQL queries.

        Args:
            natural_query: The natural language query from the user.

        Returns:
            A dictionary containing the final answer, the generated SQL query (if any), and the query results (if applicable).
        """
        logger.info(f"Processing query: {natural_query}")

        if self._verify_question(natural_query) == 'casual_interaction':
            model_response = self._answer_question_knai(self.history, natural_query)
            
            response = {
                "final_answer": model_response,
                "sql_query": None,
                "query_result": None, 
            }

            return {
                "status": "success",
                "response": response
            }

        

        sql_query = sql_generator(natural_query)

        logger.info(f"Generated SQL query: {sql_query}")

        if sql_query == "NO_CONTEXT":
            return {
                    "status": "error", 
                    "response": 
                        {
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
                with extensive experience in extracting insight and aand providing strategic recommendations. 
                Your main task is to analyze the provided data comprehensively and generate actionable insights in a human-friendly response.
                Use the query result to explain any key patterns, trends, and insights that can be derived from the data.
.
    
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

        final_answer = llmService.getwatson_llm().invoke(prompt)

        response = {
            "final_answer": final_answer.content,
            "sql_query": sql_query,
            "query_result": query_result, 
        }

        self.history.append(f"<user> {natural_query}")
        self.history.append(f"<assistant> {final_answer.content}")
        
        return {
            "status": "success",
            "response": response
        }