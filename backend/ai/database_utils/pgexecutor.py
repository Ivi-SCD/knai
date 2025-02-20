import psycopg2
from typing import List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor

class PostgresExecutor:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish database connection with dictionary cursor"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            raise Exception(f"Connection error: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries
        """
        try:
            self.connect()
            
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)
            
            # Fetch results if it's a SELECT query
            if self.cur.description:
                results = self.cur.fetchall()
                return [dict(row) for row in results]
            
            # If not SELECT, return affected rows count
            return [{"affected_rows": self.cur.rowcount}]

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Query execution error: {e}")
        
        finally:
            self.disconnect()

    def execute_transaction(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple queries in a transaction
        queries: List of dictionaries with 'query' and optional 'params' keys
        """
        try:
            self.connect()
            results = []
            
            for query_dict in queries:
                query = query_dict['query']
                params = query_dict.get('params')
                
                if params:
                    self.cur.execute(query, params)
                else:
                    self.cur.execute(query)
                
                if self.cur.description:
                    results.append(self.cur.fetchall())
                else:
                    results.append([{"affected_rows": self.cur.rowcount}])
            
            self.conn.commit()
            return results

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Transaction execution error: {e}")
        
        finally:
            self.disconnect()

