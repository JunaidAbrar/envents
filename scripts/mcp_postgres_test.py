#!/usr/bin/env python
"""
Script to test the custom PostgreSQL MCP integration.
"""
import sys
import os

# Add the project to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envents_project.settings')
django.setup()

def test_postgres_mcp():
    print("Testing PostgreSQL MCP integration...")
    
    from apps.mcp.tools import list_available_tools, call_tool
    
    # List available tools (database tables)
    print("Listing available tools (database tables)...")
    tools = list_available_tools()
    
    if not tools:
        print("No tools found or database connection failed")
        return
    
    print(f"Found {len(tools)} tables/views:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test calling a tool on a known table
    if tools:
        test_table = tools[0].name
        print(f"\nTesting query on table: {test_table}")
        results = call_tool(test_table, {})
        
        if results:
            print(f"Query returned {len(results)} rows")
            if results:
                print("Sample row:")
                for key, value in results[0].items():
                    print(f"  {key}: {value}")
        else:
            print("No results returned or error occurred")

if __name__ == "__main__":
    test_postgres_mcp()