from prompt import POSTGRES_SINTAX_RULES, AGENT_ROLE, AGENT_RULES
from langchain.prompts import PromptTemplate
from llm import get_llm

def get_query(json, question) -> str:

    import utils
    md_schema = utils.json_schema_into_md(get_llm(), json)

    template_to_query_answer = PromptTemplate(
        input_variables=["role", "rules", "json"],
        template="""
            ROLE:
                {role}

            SINTAX:
                {sintax}

            RULES:
                {rules}

            SCHEMA:
                {json}

            USER:
                {question}

            QUERY:
        """
    )

    template_formatted = template_to_query_answer.format(
        role=AGENT_ROLE,
        sintax=POSTGRES_SINTAX_RULES,
        rules=AGENT_RULES,
        question=question,
        json=md_schema
    )
    response = get_llm().invoke(template_formatted)
    return utils.extract_sql_regex(response)

def execute_sql_query(query, executor):
    result = executor.execute_query(query)
    return result