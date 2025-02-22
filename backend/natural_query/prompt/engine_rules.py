POSTGRES_SINTAX_RULES = """
1. BASIC SYNTAX:
- Use uppercase for SQL keywords (SELECT, FROM, WHERE, etc.)
- Use semicolon (;) at the end of each query
- Table and column names in lowercase
- Use single quotes ('') for strings
- Use double quotes ("") for table/column names when needed

2. BEST PRACTICES:
- Prefix columns with table name in JOINs (ex: users.id)
- Use alias for long table names (ex: SELECT u.name FROM users u)
- Align subqueries for better readability
- Use INNER JOIN instead of WHERE for relationships
- Prefer EXISTS over IN for subqueries

3. DATA TYPES:
- Dates: 'YYYY-MM-DD'
- Timestamps: 'YYYY-MM-DD HH:MI:SS'
- Text always in single quotes
- Numbers without quotes
- Booleans: TRUE or FALSE (no quotes)

4. COMMON FUNCTIONS:
- Aggregation: COUNT(), SUM(), AVG(), MAX(), MIN()
- Text: UPPER(), LOWER(), TRIM(), CONCAT()
- Date: NOW(), CURRENT_DATE, DATE_TRUNC()
- Conversion: CAST(), ::

5. OPTIMIZATION:
- Use indexes appropriately
- Avoid SELECT *
- Prefer JOINs over subqueries when possible
- Use EXPLAIN ANALYZE for performance analysis
- Limit results with LIMIT when appropriate

6. NULL CONDITIONS:
- Use IS NULL or IS NOT NULL
- Never use = NULL or != NULL
- Consider COALESCE() for default values

7. SORTING AND GROUPING:
- GROUP BY must include all non-aggregated columns
- ORDER BY can use column number (not recommended)
- Specify ASC or DESC explicitly
- Use HAVING to filter after GROUP BY
""" 