from langchain.prompts import PromptTemplate
from prompt import general_rules, roles
import json, re

def json_schema_into_md(model, json):
    template_json_into_md = PromptTemplate(
        input_variables=["role", "rules", "json"],
        template="""
        ROLE:
            {role}

        RULES: 
            {rules}

        SCHEMA: 
            {json}

        MARKDOWN:
        """
    )

    formatted_template = template_json_into_md.format(
        role=roles.JSON_TO_MARKDOWN_ROLE,
        rules=general_rules.JSON_TO_MD_RULE,
        json=json
    )

    response = model.invoke(formatted_template)

    return response  


def extract_sql_regex(text):
    try:
        pattern = r"```sql\n([\s\S]*?)\n```"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None
    except Exception as e:
        print(f"Erro ao extrair SQL: {e}")
        return None

def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
    
    return data