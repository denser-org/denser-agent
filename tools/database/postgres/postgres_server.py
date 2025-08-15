#!/usr/bin/env python3
"""
Simplified Database MCP Server
Provides database query tools via Model Context Protocol over HTTP
"""

import sys
import os
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor

# Add tools directory to path
tools_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, tools_dir)

from base_mcp_server import BaseMCPServer

# Database configuration (same as setup_analytics_demo.py)
DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "product_database",
    "user": "product_admin", 
    "password": "product123",
    "port": 5432
}

class DatabaseMCPServer(BaseMCPServer):
    """Simplified Database MCP Server implementation"""
    
    def __init__(self, port: int = 8002):
        # Define tools
        tools = [
            {
                "name": "execute_query",
                "description": "Execute a SQL query (SELECT, INSERT, UPDATE, DELETE). Returns results for SELECT queries.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        },
                        "params": {
                            "type": "array",
                            "description": "Optional parameters for parameterized queries",
                            "items": {"type": "string"},
                            "default": []
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "describe_table",
                "description": "Get the structure/schema of a database table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to describe"
                        }
                    },
                    "required": ["table_name"]
                }
            },
            {
                "name": "list_tables",
                "description": "List all tables in the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_table_data",
                "description": "Get sample data from a table with optional filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return",
                            "default": 10
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause (without the WHERE keyword)",
                            "default": ""
                        }
                    },
                    "required": ["table_name"]
                }
            }
        ]
        
        # Initialize base class
        super().__init__("database", port, tools)
        
        # Test database connection
        self._test_db_connection()
    
    def _test_db_connection(self):
        """Test database connection on startup"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            self.logger.info("✅ Database connection successful")
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
    
    
    async def execute_tool(self, name: str, arguments: dict) -> str:
        """Execute tool logic"""
        try:
            if name == "execute_query":
                return await self._execute_query(
                    arguments["query"],
                    arguments.get("params", [])
                )
            
            elif name == "describe_table":
                return await self._describe_table(arguments["table_name"])
            
            elif name == "list_tables":
                return await self._list_tables()
            
            elif name == "get_table_data":
                return await self._get_table_data(
                    arguments["table_name"],
                    arguments.get("limit", 10),
                    arguments.get("where_clause", "")
                )
            
            else:
                return f"❌ Unknown tool: {name}"
                
        except Exception as e:
            self.logger.error(f"❌ Tool error: {e}")
            return f"❌ Database error: {str(e)}"
    
    async def _execute_query(self, query: str, params: List[str] = None) -> str:
        """Execute a SQL query"""
        if params is None:
            params = []
        
        try:
            # Security check - prevent certain dangerous operations
            query_upper = query.upper().strip()
            dangerous_operations = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE USER', 'GRANT', 'REVOKE']
            for op in dangerous_operations:
                if query_upper.startswith(op):
                    return f"❌ Operation '{op}' is not allowed for security reasons"
            
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Execute query
            cursor.execute(query, params)
            
            # Handle different query types
            if query_upper.startswith('SELECT'):
                results = cursor.fetchall()
                conn.close()
                
                if not results:
                    return "📊 Query executed successfully - No results found"
                
                # Format results as markdown table
                formatted_results = f"## 📊 Query Results ({len(results)} rows)\n\n"
                
                if results:
                    # Get column names from first row
                    columns = list(results[0].keys())
                    
                    # Create markdown table header
                    formatted_results += "| " + " | ".join(columns) + " |\n"
                    formatted_results += "|" + "|".join(["---" for _ in columns]) + "|\n"
                    
                    # Add data rows
                    for row in results:
                        values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
                        formatted_results += "| " + " | ".join(values) + " |\n"
                
                formatted_results += f"\n✅ Total rows: {len(results)}"
                return formatted_results
            
            else:
                # For INSERT, UPDATE, DELETE
                affected_rows = cursor.rowcount
                conn.commit()
                conn.close()
                
                operation = query_upper.split()[0]
                return f"✅ {operation} executed successfully - {affected_rows} rows affected"
                
        except Exception as e:
            return f"❌ Query execution error: {str(e)}"
    
    async def _describe_table(self, table_name: str) -> str:
        """Get table structure"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get table schema
            query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            cursor.execute(query, (table_name,))
            
            columns = cursor.fetchall()
            conn.close()
            
            if not columns:
                return f"❌ Table '{table_name}' not found"
            
            # Format table structure as markdown
            result = f"## 📋 Table Structure: `{table_name}`\n\n"
            result += "| Column Name | Data Type | Nullable | Default | Max Length |\n"
            result += "|-------------|-----------|----------|---------|------------|\n"
            
            for col in columns:
                nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
                default = col['column_default'] or "None"
                max_len = col['character_maximum_length'] or "N/A"
                
                result += f"| {col['column_name']} | {col['data_type']} | {nullable} | {default} | {max_len} |\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error describing table: {str(e)}"
    
    async def _list_tables(self) -> str:
        """List all tables in the database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            cursor.execute(query)
            
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                return "📋 No tables found in the database"
            
            result = "## 📋 Database Tables\n\n"
            for i, table in enumerate(tables, 1):
                result += f"{i}. **{table['table_name']}**\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error listing tables: {str(e)}"
    
    async def _get_table_data(self, table_name: str, limit: int = 10, where_clause: str = "") -> str:
        """Get sample data from a table"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query
            query = f"SELECT * FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return f"📊 No data found in table '{table_name}'"
            
            # Format results as markdown table
            result = f"## 📊 Sample Data from `{table_name}` ({len(rows)} rows)\n\n"
            
            if rows:
                # Get column names from first row
                columns = list(rows[0].keys())
                
                # Create markdown table header
                result += "| " + " | ".join(columns) + " |\n"
                result += "|" + "|".join(["---" for _ in columns]) + "|\n"
                
                # Add data rows
                for row in rows:
                    values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
                    result += "| " + " | ".join(values) + " |\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error getting table data: {str(e)}"
    
    def start_server(self):
        """Start the Database MCP server"""
        tool_descriptions = [
            "execute_query - Execute SQL queries",
            "describe_table - Get table structure", 
            "list_tables - List all tables",
            "get_table_data - Get sample table data"
        ]
        super().start_server(tool_descriptions)

if __name__ == "__main__":
    server = DatabaseMCPServer()
    server.start_server()