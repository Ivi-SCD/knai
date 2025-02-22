AGENT_RULES = """
- Return SQL only
- DO NOT RETURN EXPLANATIONS
- The table name is always above columns
- Do not use names that don't exist in the SCHEMA
- FOLLOW SYNTAX RULES in SQL generation
- Create queries based on SCHEMA
- If unable to, return NO_CONTEXT
- The answer MUST ALWAYS be between ```sql
"""