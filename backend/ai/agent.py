from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

def get_toolkit(engine, llm):
    """
    Returns the toolkit.
    :param db: The database.
    :param llm: The LLM.
    
    :return:
        Tools: a list of tools.
    """
    db = SQLDatabase(engine)
    
    toolkit = SQLDatabaseToolkit(db=db,
                                 llm=llm)
    
    return toolkit.get_tools()

def get_agent_executor(engine, llm,
                       prompt):
    """
    Returns the agent executor.

    :returns:
        AgentExecutor: The agent executor.
    """
    tools = get_toolkit(engine=engine,
                        llm=llm)
    print(tools)
    return create_react_agent(llm,
                              tools=tools, 
                              prompt=prompt)