#!/usr/bin/env python3
"""
Utility script to list available tools from MCP servers
Usage: python mcp_tool_list.py [server_name] [--detailed]
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, List
from src.tools.mcp_client.mcp_client import MCPClient
from src.config.settings import get_settings


def format_tool_name(name: str, max_width: int = 40) -> str:
    """Format tool name with proper width"""
    if len(name) <= max_width:
        return name.ljust(max_width)
    return name[:max_width-3] + "..."


def format_description(description: str, max_width: int = 80) -> str:
    """Format tool description with proper width"""
    if not description:
        return "No description available"
    
    if len(description) <= max_width:
        return description
    
    # Try to break at word boundaries
    words = description.split()
    result = []
    current_line = ""
    
    for word in words:
        if len(current_line + word + " ") <= max_width:
            current_line += word + " "
        else:
            if current_line:
                result.append(current_line.strip())
                current_line = word + " "
            else:
                # Word is too long, truncate it
                result.append(word[:max_width-3] + "...")
                current_line = ""
    
    if current_line:
        result.append(current_line.strip())
    
    return "\n" + " " * 42 + ("\n" + " " * 42).join(result[1:]) if len(result) > 1 else result[0]


async def list_mcp_tools(server_name: Optional[str] = None, detailed: bool = False, json_output: bool = False):
    """List available tools from MCP server(s)"""
    
    try:
        # Initialize MCP client
        print("🔍 Connecting to MCP server(s)..." if not json_output else "", file=sys.stderr if json_output else sys.stdout)
        
        client = MCPClient()
        
        # Get available servers
        available_servers = list(client.config["servers"].keys())
        enabled_servers = [name for name, config in client.config["servers"].items() if config.get("enabled", True)]
        
        if server_name and server_name not in available_servers:
            print(f"❌ Server '{server_name}' not found in configuration.")
            print(f"Available servers: {', '.join(available_servers)}")
            return False
        
        if server_name and server_name not in enabled_servers:
            print(f"⚠️  Server '{server_name}' is disabled in configuration.")
            return False
        
        # Get tools
        async with client:
            tools = await client.get_tools(server_name)
            
            if json_output:
                # JSON output format
                tools_data = []
                for tool in tools:
                    tool_data = {
                        "name": tool.name,
                        "description": tool.description or "No description available"
                    }
                    if detailed and hasattr(tool, 'args_schema') and tool.args_schema:
                        try:
                            # Get schema information
                            schema = tool.args_schema.model_json_schema() if hasattr(tool.args_schema, 'model_json_schema') else {}
                            tool_data["schema"] = schema
                        except Exception:
                            tool_data["schema"] = "Schema not available"
                    
                    tools_data.append(tool_data)
                
                result = {
                    "server": server_name or "all",
                    "total_tools": len(tools),
                    "tools": tools_data
                }
                print(json.dumps(result, indent=2))
                return True
            
            # Console output format
            if not tools:
                server_display = f" from server '{server_name}'" if server_name else ""
                print(f"🔍 No tools found{server_display}")
                return True
            
            # Header
            server_display = f" from server '{server_name}'" if server_name else f" from {len(enabled_servers)} server(s)"
            print(f"\n📋 Available MCP Tools{server_display}")
            print(f"Found {len(tools)} tool(s)\n")
            
            if detailed:
                # Detailed view with descriptions and schemas
                print("=" * 120)
                for i, tool in enumerate(tools, 1):
                    print(f"{i:3d}. {tool.name}")
                    print(f"     Description: {tool.description or 'No description available'}")
                    
                    # Try to get schema information
                    if hasattr(tool, 'args_schema') and tool.args_schema:
                        try:
                            if hasattr(tool.args_schema, 'model_fields'):
                                fields = tool.args_schema.model_fields
                                if fields:
                                    print(f"     Parameters:")
                                    for field_name, field_info in fields.items():
                                        field_desc = getattr(field_info, 'description', 'No description')
                                        field_type = getattr(field_info, 'annotation', 'unknown')
                                        print(f"       - {field_name}: {field_type} - {field_desc}")
                                else:
                                    print(f"     Parameters: None")
                            else:
                                print(f"     Parameters: Schema available but not readable")
                        except Exception as e:
                            print(f"     Parameters: Could not read schema ({e})")
                    else:
                        print(f"     Parameters: No schema available")
                    
                    print("-" * 120)
            else:
                # Simple table view
                print(f"{'#':>3} {'Tool Name':<40} {'Description'}")
                print("=" * 120)
                
                for i, tool in enumerate(tools, 1):
                    name = format_tool_name(tool.name, 40)
                    desc = format_description(tool.description or "No description available", 75)
                    print(f"{i:3d} {name} {desc}")
            
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        return False


def show_server_info():
    """Show available servers"""
    try:
        client = MCPClient()
        servers = client.config["servers"]
        
        print("🌐 Available MCP Servers:")
        print("=" * 80)
        
        for name, config in servers.items():
            status = "✅ Enabled" if config.get("enabled", True) else "❌ Disabled"
            description = config.get("description", "No description")
            command = config.get("command", "Unknown command")
            
            print(f"Server: {name}")
            print(f"  Status: {status}")
            print(f"  Description: {description}")
            print(f"  Command: {command}")
            print(f"  Tool Prefix: {config.get('tool_prefix', 'none')}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error reading server configuration: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="List available tools from MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_tool_list.py                    # List all tools from all servers
  python mcp_tool_list.py github             # List tools from GitHub server only
  python mcp_tool_list.py github --detailed  # List tools with detailed information
  python mcp_tool_list.py --servers          # Show available servers
  python mcp_tool_list.py github --json      # Output in JSON format
        """
    )
    
    parser.add_argument(
        "server_name", 
        nargs="?", 
        help="Name of the MCP server (e.g., 'github'). If not specified, lists tools from all servers."
    )
    
    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Show detailed information including tool schemas"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    parser.add_argument(
        "--servers", "-s",
        action="store_true",
        help="Show available servers and exit"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information on errors"
    )
    
    args = parser.parse_args()
    
    # Show servers and exit
    if args.servers:
        show_server_info()
        return
    
    # Run the tool listing
    success = asyncio.run(list_mcp_tools(
        server_name=args.server_name,
        detailed=args.detailed,
        json_output=args.json
    ))
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
