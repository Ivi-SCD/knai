from config import global_settings
from typing import Dict, Any
import psycopg2
import json

class SchemaExtractor:
    def __init__(self):
        self._schema_cache: Dict[str, Any] = {}
        self.conn = None
        self.cur = None
        self.connection_string = f'postgresql://{global_settings.DB_USER}:{global_settings.DB_PASSWORD}@{global_settings.DB_HOST}:{global_settings.DB_PORT}/{global_settings.DB_NAME}'
    
    def _connect(self):
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cur = self.conn.cursor()
        except Exception as e:
            raise Exception(f"Connection error: {e}")

    def _disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_schema(self, schema_name: str = 'public') -> Dict:
        """
        Extract database schema and return in the same format as your JSON schema
        """
        try:
            self._connect()
            
            # Query to get tables and their columns with types and constraints
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

            # Get foreign key relationships
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

            # Organize the schema data
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

                # Process constraints
                constraints_list = []
                if constraints:
                    constraints_list = [c.strip() for c in constraints.split(',')]

                # Build column definition
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

            # Add foreign key relationships
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
        Extract schema and save to JSON file
        """
        schema = self.get_schema(schema_name)
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=4)