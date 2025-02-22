from .prompt import POSTGRES_SINTAX_RULES, AGENT_ROLE, AGENT_RULES
from .core.schema_extractor import SchemaExtractor
from .services.llm_service import llmService
from .services.pg_service import PostgresDB
from config import global_settings
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sql_generator(natural_query: str) -> str:
    """
    Generates SQL from natural language query.
    Args:
        natural_query: The natural language query to convert
    Returns:
        Generated SQL query or "NO_CONTEXT" on error
    """
    logger.info(f'NATURAL QUERY SQL GENERATOR (QUERY): {natural_query}')
    
    try:
        extractor = SchemaExtractor()
        schema = extractor.get_schema()

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
        
        llm = llmService.getwatson_llm()
        response = llm.invoke(template)
        
        # More robust response handling
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
            
        # Extract SQL from the response
        sql_matches = re.findall(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
        if sql_matches:
            sql_query = sql_matches[0].strip()
        else:
            # If no SQL block found, try to use the whole response
            sql_query = response_text
            
        # Clean and format the query
        sql_query = " ".join(line.strip() for line in sql_query.splitlines())
        
        # Basic validation
        if not sql_query.lower().strip().startswith('select'):
            logger.warning(f"Generated query doesn't look like a SELECT statement: {sql_query}")
            return "NO_CONTEXT"
            
        return sql_query
        
    except Exception as e:
        logger.error(f"Error in sql_generator: {str(e)}")
        return "NO_CONTEXT"


def execute_query(query: str) -> str: 
    """
    Executes SQL SELECT queries safely.
    Args:
        query: The SQL query to execute (must be SELECT only)
    Returns:
        Query results as JSON string or error message
    """
    logger.info(f'EXECUTION OF QUERY: {query}')

    try:
        # Validate query is SELECT only
        if not query.lower().strip().startswith('select'):
            error_msg = "Only SELECT queries are allowed"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

        db_config = {
            'dbname': global_settings.DB_NAME,
            'user': global_settings.DB_USER,
            'password': global_settings.DB_PASSWORD,
            'host': global_settings.DB_HOST,
            'port': global_settings.DB_PORT
        }
        
        db = PostgresDB(**db_config)
        results = db.execute_select(query.lower())
        
        if not results:
            return json.dumps({"message": "Query executed successfully but returned no results"})
            
        return json.dumps(results, indent=4)

    except Exception as e:
        error_msg = f'Error executing query: {str(e)}'
        logger.error(error_msg)
        return json.dumps({"error": error_msg})