POSTGRES_SINTAX_RULES = """
1. SINTAXE BÁSICA:
- Use maiúsculas para palavras-chave SQL (SELECT, FROM, WHERE, etc.)
- Use ponto e vírgula (;) ao final de cada consulta
- Nomes de tabelas e colunas em minúsculas
- Use aspas simples ('') para strings
- Use aspas duplas ("") para nomes de tabelas/colunas quando necessário

2. BOAS PRÁTICAS:
- Prefixe colunas com nome da tabela em JOINs (ex: usuarios.id)
- Use alias para nomes longos de tabelas (ex: SELECT u.nome FROM usuarios u)
- Alinhe subconsultas para melhor legibilidade
- Use INNER JOIN ao invés de WHERE para relacionamentos
- Prefira EXISTS ao invés de IN para subconsultas

3. TIPOS DE DADOS:
- Datas: 'YYYY-MM-DD'
- Timestamps: 'YYYY-MM-DD HH:MI:SS'
- Textos sempre entre aspas simples
- Números sem aspas
- Booleanos: TRUE ou FALSE (sem aspas)

4. FUNÇÕES COMUNS:
- Agregação: COUNT(), SUM(), AVG(), MAX(), MIN()
- Texto: UPPER(), LOWER(), TRIM(), CONCAT()
- Data: NOW(), CURRENT_DATE, DATE_TRUNC()
- Conversão: CAST(), ::

5. OTIMIZAÇÃO:
- Use índices apropriadamente
- Evite SELECT *
- Prefira JOINs a subconsultas quando possível
- Use EXPLAIN ANALYZE para análise de performance
- Limite resultados com LIMIT quando apropriado

6. CONDIÇÕES NULL:
- Use IS NULL ou IS NOT NULL
- Nunca use = NULL ou != NULL
- Considere COALESCE() para valores padrão

7. ORDENAÇÃO E AGRUPAMENTO:
- GROUP BY deve incluir todas colunas não agregadas
- ORDER BY pode usar número da coluna (não recomendado)
- Especifique ASC ou DESC explicitamente
- Use HAVING para filtrar após GROUP BY
""" 