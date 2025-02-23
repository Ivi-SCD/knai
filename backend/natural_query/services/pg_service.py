from typing import List, Dict, Any, Optional
from beeai_framework.utils import BeeLogger
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import psycopg2.pool
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        Initialize the connecticon with Postgres
        Args:
            dbname: Name of database
            user: Database user
            password: Database password
            host: Database host
            port: Database port (default: 5432)
            min_connections: Pool min connections (default: 1)
            max_connections: Pool max connections (default: 10)
        """
        self.db_config = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        
        self.pool = psycopg2.pool.SimpleConnectionPool(
            min_connections,
            max_connections,
            **self.db_config
        )
        logger.info("Pool de conexões PostgreSQL inicializado")

    def close(self):
        """
        Close pool connection
        """
        if self.pool:
            self.pool.closeall()
            logger.info("Pool de conexões PostgreSQL fechado")

    @contextmanager
    def get_connection(self):
        """
        Context manager to obtain pool connection.
        Yields:
            psycopg2.connection: Connection pool
        """
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Context manager to get cursor
        Args:
            cursor_factory: cursor factory (default: RealDictCursor to return dicts)
        Yields:
            psycopg2.cursor: to execute queries
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
        Verifies if select is valid
        Args:
            query: SQL Query to be verified
        Returns:
            bool: True if is valid SELECT
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
        Execute a SQL Query securely
        Args:
            query: Query SQL (Must be SELECT)
            params: Params to query (opcional)
        Returns:
            List[Dict]: Query results
        Raises:
            ValueError: If query wasn't valid
        """

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
        Get schema infos of database
        Returns:
            Dict[str, Any]: Schema informations
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