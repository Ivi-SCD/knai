import json, re

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