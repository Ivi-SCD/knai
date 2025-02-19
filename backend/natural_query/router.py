from fastapi import APIRouter, Depends

from langgraph.graph.graph import CompiledGraph

from natural_query.dependencies import get_sql_agent
from natural_query.schemas import NaturalQueryRequest

router = APIRouter()

@router.post("/")
def query(query: NaturalQueryRequest,
          agent_executor: CompiledGraph = Depends(get_sql_agent)):
    """
    Queries the database.
    :param query: The query in natural language.
    :return:
        dict: The result of the query.
    """
    query_result = agent_executor.invoke({"messages": [("user", query.query)]})
    return query_result
    
