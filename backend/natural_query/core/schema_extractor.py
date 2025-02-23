from config import global_settings
from typing import Dict, Any
import psycopg2
import json

class SchemaExtractor:
    """
    A class to extract database schema information from a PostgreSQL database and save it to a JSON file.
    """

    def __init__(self):
        """
        Initializes the SchemaExtractor instance, setting up the connection parameters and cache.
        """

        self._schema_cache: Dict[str, Any] = {}
        self.conn = None
        self.cur = None
        self.connection_string = f'postgresql://{global_settings.DB_USER}:{global_settings.DB_PASSWORD}@{global_settings.DB_HOST}:{global_settings.DB_PORT}/{global_settings.DB_NAME}'
    
    def _connect(self):
        """
        Establishes the connection to the PostgreSQL database.
        
        Raises:
            Exception: If the connection to the database fails.
        """

        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cur = self.conn.cursor()
        except Exception as e:
            raise Exception(f"Connection error: {e}")

    def _disconnect(self):
        """
        Closes the database cursor and connection.
        """

        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_schema(self, schema_name: str = 'public') -> Dict:
        """
        Extracts the database schema, including tables, columns, and relationships (foreign keys), and returns it in JSON format.
        
        Args:
            schema_name: The name of the schema to extract (default is 'public').

        Returns:
            A dictionary containing the schema information.
        
        Raises:
            Exception: If an error occurs during schema extraction.
        """

        try:
            self._connect()
            
            schema_query = """
                SELECT 
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    (
                        SELECT string_agg(constraint_type, ', ')
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.constraint_column_usage ccu 
                            ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.table_name = t.table_name 
                        AND ccu.column_name = c.column_name
                    ) as constraints
                FROM information_schema.tables t
                JOIN information_schema.columns c 
                    ON t.table_name = c.table_name
                WHERE t.table_schema = %s
                    AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position;
            """
            
            self.cur.execute(schema_query, (schema_name,))
            results = self.cur.fetchall()

            fk_query = """
                SELECT
                    tc.table_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s;
            """
            
            self.cur.execute(fk_query, (schema_name,))
            foreign_keys = self.cur.fetchall()

            schema = {}
            current_table = None

            for row in results:
                table_name, column_name, data_type, is_nullable, default, max_length, constraints = row
                
                if table_name != current_table:
                    current_table = table_name
                    schema[table_name] = {
                        "columns": {},
                        "relationships": []
                    }

                constraints_list = []
                if constraints:
                    constraints_list = [c.strip() for c in constraints.split(',')]
  
                column_def = {
                    "type": data_type,
                    "required": is_nullable == 'NO',
                    "constraints": constraints_list
                }

                if default is not None:
                    column_def["default"] = default
                if max_length is not None:
                    column_def["max_length"] = max_length

                schema[table_name]["columns"][column_name] = column_def

            for fk in foreign_keys:
                table_name, column_name, foreign_table, foreign_column = fk
                if table_name in schema:
                    schema[table_name]["relationships"].append({
                        "from": column_name,
                        "to": f"{foreign_table}.{foreign_column}"
                    })

            return schema

        except Exception as e:
            raise Exception(f"Schema extraction error: {e}")
        
        finally:
            self._disconnect()

    def save_schema_to_file(self, output_file: str, schema_name: str = 'public'):
        """
        Extracts the schema and saves it to a JSON file.
        
        Args:
            output_file: The file path where the schema will be saved.
            schema_name: The schema to extract (default is 'public').
        """
        
        schema = self.get_schema(schema_name)
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=4)