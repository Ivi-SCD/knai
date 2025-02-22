from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from .tools import sql_generator, execute_query, analyze_query_performance
from beeai_framework.agents.types import BeeInput, BeeRunInput
from beeai_framework.backend.chat import ChatModel
from beeai_framework.utils import BeeLogger
from .services.llm_service import llmService
from beeai_framework import BeeAgent
from typing import Dict, Any

logger = BeeLogger(__name__)

class KNAIService:

    
    def __init__(self):
        self.chat_model = None
        self.agent = None


    async def initialize(self):
        """
        Initialize the chat model and agent
        """
        if not self.chat_model:
            self.chat_model = await ChatModel.from_name("ollama:granite3.1-dense:8b")
            self.agent = BeeAgent(
                BeeInput(
                    llm=self.chat_model,
                    tools=[sql_generator, execute_query, analyze_query_performance],
                    memory=UnconstrainedMemory()
                )
            )


    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return structured results
        """
        await self.initialize()

        try:
            result = await self.agent.run(
                BeeRunInput(
                    prompt=self._create_prompt(query)
                )
            )

            logger.info(result)
            return self._format_response(result)

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "status": "error",
                "response": {
                    "message": str(e)}
            }


    def _create_prompt(self, query: str) -> str:
        """
        Create the system prompt
        """
        return f"""
        <|system|>
            You are KNAI, an AI assistant specialized in SQL analysis and generation of insights.
            Follow these steps for each query:
            1. Generate and validate SQL using sql_generator
            2. Execute query with execute_query
            3. Analyze query performance with analyze_query_performance

        <|tools|>
            - sql_generator: Creates SQL queries
            - execute_query: Executes queries safely
            - analyze_query_performance: Analyzes query efficiency

        <|rule|>
            1. Always validate queries before execution
            2. Cache frequently used query results
            3. Include performance metrics when relevant
            4. Format responses using markdown

        <|user|>
            {query}

        <|assistant|>
        """

    
    def _create_final_answer_tunned(self, context) -> str:
        """
        Tunning the final answer
        """
        return f"""
            <|context|>
                {context}

            <|system|>
            You are an expert data analyst with extensive experience in extracting insights and providing strategic recommendations. Your task is to analyze the provided data comprehensively.
            Follow these guidelines when analyzing the data:

            DATA EXAMINATION
            INSIGHT GENERATION
            RECOMMENDATIONS
            ANALYSIS STRUCTURE

            <|assistant|>
        """
    

    def _format_response(self, result) -> Dict[str, Any]:
        """
        Format the agent's response for the API
        """
        steps = []
        final_answer = None
        generated_sql = None
        execution_result = None
        performance_analysis = None
        template_final_answer_tunned = self._create_final_answer_tunned(result)

        final_answer_tunned = llmService.get_llm().invoke(template_final_answer_tunned)

        
        for iteration in result.iterations:
            step = {
                "thought": iteration.state.thought,
                "tool_name": iteration.state.tool_name,
                "tool_output": iteration.state.tool_output
            }
            steps.append(step)

            # Capture specific outputs
            if iteration.state.tool_name == "sql_generator":
                generated_sql = iteration.state.tool_output

            elif iteration.state.tool_name == "execute_query":
                execution_result = iteration.state.tool_output

            elif iteration.state.tool_name == "analyze_query_performance":
                performance_analysis = iteration.state.tool_output

            if iteration.state.final_answer:
                final_answer = iteration.state.final_answer

        return {
            "status": "success",
            "response": {
                "final_answer": final_answer or result.result,
                "final_answer_tunned": final_answer_tunned,
                "steps": steps,
                "details": {
                    "generated_sql": generated_sql,
                    "execution_result": execution_result,
                    "performance_analysis": performance_analysis
                }
            }
        }