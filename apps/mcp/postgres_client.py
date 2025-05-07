"""
Direct PostgreSQL integration for MCP functionality.

This module provides direct connectivity to the PostgreSQL database
without relying on the MCP client library, which may have import issues.
"""
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings

logger = logging.getLogger(__name__)

class PostgresMCPClient:
    """
    A simple client that connects directly to PostgreSQL to provide MCP-like functionality.
    """
    
    def __init__(self, name="Envents App", version="1.0.0"):
        """Initialize the PostgreSQL MCP client."""
        self.name = name
        self.version = version
        self.connection = None
        self.connected = False
    
    def connect(self):
        """Connect to the PostgreSQL database using settings from Django."""
        try:
            if not hasattr(settings, 'MCP_CONFIG') or 'mcpServers' not in settings.MCP_CONFIG:
                logger.error("MCP configuration missing in Django settings")
                return False
                
            postgres_config = settings.MCP_CONFIG['mcpServers'].get('postgres')
            if not postgres_config:
                logger.error("PostgreSQL MCP server configuration missing")
                return False
            
            # Extract the connection string from the args
            connection_string = None
            for arg in postgres_config.get('args', []):
                if isinstance(arg, str) and arg.startswith('postgresql://'):
                    connection_string = arg
                    break
            
            if not connection_string:
                logger.error("PostgreSQL connection string not found in MCP configuration")
                return False
                
            # Connect to PostgreSQL directly
            self.connection = psycopg2.connect(connection_string)
            self.connected = True
            logger.info(f"Connected to PostgreSQL database for MCP: {self.name} v{self.version}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to connect to PostgreSQL: {str(e)}")
            return False
    
    def list_tools(self):
        """List all tools (tables/views) available in the database."""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Query database for tables/views
                cursor.execute("""
                    SELECT table_name as name, 
                           'Database table' as description,
                           table_schema as "schema"
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                """)
                tools = cursor.fetchall()
                
                # Convert to a list of Tool objects with name and description
                return [Tool(item['name'], item['description']) for item in tools]
                
        except Exception as e:
            logger.exception(f"Error listing tools: {str(e)}")
            return []
    
    def call_tool(self, tool_name, parameters=None):
        """
        Call a tool (query a table/view) with parameters.
        
        Args:
            tool_name (str): The name of the table/view to query
            parameters (dict): Parameters to filter the query
            
        Returns:
            dict: The result of the query
        """
        if not self.connected:
            if not self.connect():
                return None
                
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Basic query structure - could be extended for more complex queries
                query = f"SELECT * FROM {tool_name}"
                
                # Add WHERE clauses for parameters
                params = []
                if parameters:
                    where_clauses = []
                    for key, value in parameters.items():
                        where_clauses.append(f"{key} = %s")
                        params.append(value)
                    
                    if where_clauses:
                        query += " WHERE " + " AND ".join(where_clauses)
                
                # Execute the query
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # Convert to a list of dictionaries
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.exception(f"Error calling tool {tool_name}: {str(e)}")
            return None
    
    def close(self):
        """Close the database connection."""
        if self.connected and self.connection:
            self.connection.close()
            self.connected = False
            logger.info("Closed PostgreSQL MCP connection")


class Tool:
    """Simple tool class to mimic MCP tool structure."""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description