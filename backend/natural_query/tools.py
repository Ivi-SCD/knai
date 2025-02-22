from .prompt import POSTGRES_SINTAX_RULES, AGENT_ROLE, AGENT_RULES
from beeai_framework.tools.tool import StringToolOutput
from .core.schema_extractor import SchemaExtractor
from .services.llm_service import llmService
from .services.pg_service import PostgresDB
from beeai_framework.utils import BeeLogger
from config import global_settings
from beeai_framework import tool
import json

logger = BeeLogger(__name__)

@tool
def sql_generator(natural_query: str) -> StringToolOutput:
    """
    Generates SQL from natural language query.
    Args:
        natural_query: The natural language query to convert
    Returns:
        Generated SQL query
    """
    
    extractor = SchemaExtractor()
    schema =  extractor.get_schema()

    try:
        template = f"""
        <|system|>:
            {AGENT_ROLE}
        <|sintax|>:
            {POSTGRES_SINTAX_RULES}
        <|rules|>:
            {AGENT_RULES}
        <|schema|>:
            {schema}
        <|user|>
            {natural_query}
        <|assistant|>
        """
        
        llm = llmService.get_llm()
        response = llm.invoke(template)
        response_query = response.replace('```sql', '').replace('```', '')
        response_query_inline = " ".join(line.strip() for line in response_query.splitlines())

        return StringToolOutput(response_query_inline)
        
    except Exception as e:
        logger.error(f"Error in sql_generator: {str(e)}")
        return StringToolOutput("NO_CONTEXT")


@tool
def execute_query(natural_query):
    """
    Executes SQL SELECT queries safely.
    Args:
        natural_query: The SQL query to execute (must be SELECT only)
    Returns:
        Query results as JSON string
    """
    db_config = {
        'dbname': global_settings.DB_NAME,
        'user': global_settings.DB_USER,
        'password': global_settings.DB_PASSWORD,
        'host': global_settings.DB_HOST,
        'port': global_settings.DB_PORT
    }
    
    natural_query_lower = natural_query.lower()

    db = PostgresDB(**db_config)
    try:
        results = db.execute_select(natural_query_lower)
        return StringToolOutput(json.dumps(results, indent=4))

    except Exception as e:
        logger.error(f'Error executing query: {str(e)}')


@tool
def analyze_query_performance(query: str) -> StringToolOutput:
    """
    Analyzes query performance using EXPLAIN ANALYZE.
    Args:
        query: SQL query to analyze
    Returns:
        Performance analysis results as a string
    """
    
    try:

        db_config = {
            'dbname': global_settings.DB_NAME,
            'user': global_settings.DB_USER,
            'password': global_settings.DB_PASSWORD,
            'host': global_settings.DB_HOST,
            'port': global_settings.DB_PORT
        }
            
        db = PostgresDB(**db_config)
        explain_query = f"EXPLAIN ANALYZE {query}"
        logger.info(f'Analyze query perfomance: {explain_query}')
        results = db.execute_select(explain_query)
        
        return StringToolOutput(json.dumps(results, indent=2))
        
    except Exception as e:
        logger.error(f"Error analyzing query performance: {str(e)}")
        return StringToolOutput(f"Error analyzing query performance: {str(e)}")
