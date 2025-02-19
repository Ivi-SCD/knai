from fastapi import Depends
from sqlalchemy import Engine

from dependencies import get_sync_engine
from ai.agent import get_agent_executor
from ai.llm import get_llm

def get_sql_agent(engine: Engine = Depends(get_sync_engine)):
     """
     Returns the SQL agent.
     
     :param db: The database session.
     :return:
         SQLAgent: The SQL agent.
     """
     llm = get_llm()
     
     prompt = """
     Você é um agente virtual de um banco de dados. Você é capaz de realizar consultas em um banco de dados relacional.
     Você possui a tool para executar consultas SQL em um banco de dados.
     
     Ao receber uma pergunta do usuário, você deverá:
     1. Identificar a tabela e as colunas que contém a informação que o usuário está buscando
     2. Criar uma consulta SQL para recuperar os dados que o usuário está buscando.
     3. Executar a consulta SQL no banco de dados e retornar o resultado para o usuário
     
     Você deve responder apenas com o resultado da consulta SQL.
     Você não deve responder com nenhum texto além do resultado da consulta SQL.
     
     O banco de dados que você está conectado é um banco de dados relacional.
     Banco de dados: PostgreSQL
     
     Esquema do banco de dados:
     CREATE TABLE "Customer" (
        "CustomerId" SERIAL PRIMARY KEY, 
        "FirstName" VARCHAR(40) NOT NULL, 
        "LastName" VARCHAR(20) NOT NULL, 
        "Company" VARCHAR(80), 
        "Address" VARCHAR(70), 
        "City" VARCHAR(40), 
        "State" VARCHAR(40), 
        "Country" VARCHAR(40), 
        "PostalCode" VARCHAR(10), 
        "Phone" VARCHAR(24), 
        "Fax" VARCHAR(24), 
        "Email" VARCHAR(60) NOT NULL
     );
     
     
     """
     
     agent_executor = get_agent_executor(engine=engine, llm=llm,
                                         prompt=prompt.format(dialect=engine.dialect.name, top_k=5))
     print('agent_executor: ', agent_executor)
     return agent_executor