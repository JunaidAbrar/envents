import logging
from .postgres_client import PostgresMCPClient

logger = logging.getLogger(__name__)

def get_mcp_client():
    """
    Returns a configured MCP client connected to the PostgreSQL database.
    """
    client = PostgresMCPClient(name="Envents App", version="1.0.0")
    client.connect()
    return client

def list_available_tools():
    """
    Returns a list of all available tools from the MCP server.
    """
    client = get_mcp_client()
    if not client:
        logger.error("Failed to get MCP client")
        return []
    
    try:
        tools = client.list_tools()
        return tools
    except Exception as e:
        logger.exception(f"Error listing MCP tools: {str(e)}")
        return []
    finally:
        client.close()

def call_tool(tool_name, parameters=None):
    """
    Calls a specific MCP tool with the given parameters.
    
    Args:
        tool_name (str): The name of the tool to call
        parameters (dict): The parameters to pass to the tool
        
    Returns:
        dict: The result of the tool call
    """
    client = get_mcp_client()
    if not client:
        logger.error("Failed to get MCP client")
        return None
    
    try:
        if parameters is None:
            parameters = {}
        
        result = client.call_tool(tool_name, parameters)
        return result
    except Exception as e:
        logger.exception(f"Error calling MCP tool '{tool_name}': {str(e)}")
        return None
    finally:
        client.close()