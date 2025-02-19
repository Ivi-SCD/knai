from langchain.prompts import PromptTemplate
from prompt import general_rules, roles
import json

def json_schema_into_md(model, json):
    model = model

    template_json_into_md = PromptTemplate(
        input_variables=["role", "rules", "examples", "json"],
        template="""
        ROLE:
            {role}

        RULES: 
            {rules}
        
        EXAMPLES:
            {examples}

        SCHEMA: 
            {json}

        AGENT:
        """
    )

    formatted_template = template_json_into_md.format(
        role=roles.JSON_TO_MARKDOWN_ROLE,
        examples="""    
        TABELA usuario
            COLUNA id TIPO SERIAL PRIMARY KEY TRUE
            COLUNA nome TIPO VARCHAR TAMANHO 20 NULO FALSE  
        """,
        rules=general_rules.JSON_TO_MD_RULE,
        json=json
    )

    return model.invoke(formatted_template).content

def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
    
    return data