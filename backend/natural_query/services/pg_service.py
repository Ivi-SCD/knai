from typing import List, Dict, Any, Optional
from beeai_framework.utils import BeeLogger
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import psycopg2.pool
import psycopg2

logger = BeeLogger(__name__)

class PostgresDB:
    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str,
        port: int = 5432,
        min_connections: int = 1,
        max_connections: int = 10
    ):
        """
        Inicializa a conexão com o Postgres.
        Args:
            dbname: Nome do banco de dados
            user: Usuário do banco
            password: Senha do banco
            host: Host do banco
            port: Porta do banco (default: 5432)
            min_connections: Mínimo de conexões no pool (default: 1)
            max_connections: Máximo de conexões no pool (default: 10)
        """
        self.db_config = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        
        # Inicializa o pool de conexões
        self.pool = psycopg2.pool.SimpleConnectionPool(
            min_connections,
            max_connections,
            **self.db_config
        )
        logger.info("Pool de conexões PostgreSQL inicializado")

    def close(self):
        """Fecha o pool de conexões"""
        if self.pool:
            self.pool.closeall()
            logger.info("Pool de conexões PostgreSQL fechado")

    @contextmanager
    def get_connection(self):
        """
        Context manager para obter uma conexão do pool.
        Yields:
            psycopg2.connection: Conexão do pool
        """
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Context manager para obter um cursor.
        Args:
            cursor_factory: Fábrica de cursor (default: RealDictCursor para retornar dicts)
        Yields:
            psycopg2.cursor: Cursor para executar queries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def is_select_query(self, query: str) -> bool:
        """
        Verifica se a query é um SELECT válido.
        Args:
            query: Query SQL a ser verificada
        Returns:
            bool: True se for um SELECT válido
        """
        query = query.lower().strip()
        
        forbidden_commands = [
            'insert', 'update', 'delete', 'drop', 'truncate', 
            'alter', 'create', 'replace', 'merge', 'upsert',
            'grant', 'revoke', 'commit', 'rollback'
        ]
        
        if query.startswith('explain'):
            return True

        if not query.startswith('select'):
            return False
        
        
        return not any(cmd in query for cmd in forbidden_commands)

    def execute_select(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Executa uma query SELECT de forma segura.
        Args:
            query: Query SQL (deve ser SELECT)
            params: Parâmetros para a query (opcional)
        Returns:
            List[Dict]: Resultados da query
        Raises:
            ValueError: Se a query não for um SELECT válido
        """
        # Valida a query
        if not self.is_select_query(query):
            raise ValueError("Only SELECT queries are allowed")

        try:
            with self.get_cursor() as cursor:
                # Executa a query
                cursor.execute(query, params or {})
                results = cursor.fetchall()
                return results

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o schema do banco.
        Returns:
            Dict[str, Any]: Informações do schema
        """
        schema_query = """
        SELECT 
            t.table_name,
            json_agg(
                json_build_object(
                    'column_name', c.column_name,
                    'data_type', c.data_type,
                    'is_nullable', c.is_nullable,
                    'column_default', c.column_default
                )
            ) as columns
        FROM 
            information_schema.tables t
            JOIN information_schema.columns c ON c.table_name = t.table_name
        WHERE 
            t.table_schema = 'public'
        GROUP BY 
            t.table_name;
        """
        
        try:
            return self.execute_select(schema_query)
        except Exception as e:
            logger.error(f"Error getting schema info: {str(e)}")
            raise