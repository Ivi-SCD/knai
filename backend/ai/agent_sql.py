from prompt import POSTGRES_SINTAX_RULES, AGENT_ROLE, AGENT_RULES
from langchain.prompts import PromptTemplate
from llm import get_llm
import json

def get_query(path, question) -> str:
    import utils

    with open(path, 'r') as file:
        data = json.load(file)

    md_schema = utils.json_schema_into_md(get_llm(), data)

    template_to_query_answer = PromptTemplate(
        input_variables=["role", "rules", "json"],
        template="""
            ROLE:
                {role}

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
        rules=POSTGRES_SINTAX_RULES.join("\n" + AGENT_RULES),
        question=question,
        json=md_schema
    )
    
    return get_llm().invoke(template_formatted).content