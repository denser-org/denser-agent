#!/usr/bin/env python3
"""
Simplified MCP Tools Manager
Centralized management for multiple MCP servers and their tools
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-tools-manager")


class MCPToolsManager:
    """Simplified manager for multiple MCP servers and their tools"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "mcp.json")
        self.config_file = config_file
        self.servers = {}
        self.tools = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load MCP server configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            mcp_servers = config.get('mcpServers', {})
            for server_name, server_config in mcp_servers.items():
                transport = server_config.get('transport', {})
                self.servers[server_name] = {
                    'name': server_name,
                    'base_url': transport.get('baseUrl', ''),
                    'endpoints': transport.get('endpoints', {}),
                    'description': server_config.get('description', '')
                }
            
            logger.info(f"✅ Loaded {len(self.servers)} MCP servers from {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load MCP configuration: {e}")
    

    async def discover_tools(self) -> Dict[str, List[Dict]]:
        """Discover all available tools from all MCP servers"""
        all_tools = {}
        for server_name, server in self.servers.items():
            try:
                tools = await self._get_server_tools(server)
                all_tools[server_name] = tools
                
                # Add to global tools registry
                for tool in tools:
                    self.tools[tool['name']] = tool
                
                logger.info(f"✅ Discovered {len(tools)} tools from {server_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to discover tools from {server_name}: {e}")
                all_tools[server_name] = []
        
        return all_tools
    
    async def _get_server_tools(self, server: Dict) -> List[Dict]:
        """Get tools from a specific MCP server"""
        async with httpx.AsyncClient() as client:
            url = f"{server['base_url']}{server['endpoints']['listTools']}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            tools = data.get('tools', [])
            
            # Add server info to each tool
            for tool in tools:
                tool['server_name'] = server['name']
                tool['server_url'] = server['base_url']
            
            return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool by name"""
        if tool_name not in self.tools:
            available_tools = list(self.tools.keys())
            return f"❌ Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}"
        
        tool = self.tools[tool_name]
        server = self.servers[tool['server_name']]
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{server['base_url']}{server['endpoints']['callTool']}"
                payload = {"name": tool_name, "arguments": arguments}
                
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                return result["content"][0]["text"]
                
        except Exception as e:
            logger.error(f"❌ Tool call error for {tool_name}: {e}")
            return f"❌ Error calling {tool_name}: {str(e)}"
    
    async def get_all_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get all tools formatted for LLM use (Anthropic format)"""
        await self.discover_tools()
        
        anthropic_tools = []
        for tool in self.tools.values():
            anthropic_tools.append({
                "name": tool['name'],
                "description": f"[{tool['server_name']}] {tool['description']}",
                "input_schema": tool['inputSchema']
            })
        
        return anthropic_tools
    
    async def check_servers_health(self) -> Dict[str, bool]:
        """Check health of all MCP servers"""
        health_status = {}
        
        for server_name, server in self.servers.items():
            try:
                async with httpx.AsyncClient() as client:
                    url = f"{server['base_url']}{server['endpoints']['health']}"
                    response = await client.get(url, timeout=5.0)
                    health_status[server_name] = response.status_code == 200
            except:
                health_status[server_name] = False
        
        return health_status
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a specific tool"""
        return self.tools.get(tool_name)
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """Get information about a specific server"""
        return self.servers.get(server_name)
    
    def list_tools_by_server(self) -> Dict[str, List[str]]:
        """List all tools grouped by server"""
        tools_by_server = {}
        
        for tool_name, tool in self.tools.items():
            server_name = tool['server_name']
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append(tool_name)
        
        return tools_by_server
    
    async def add_server(self, server_name: str, base_url: str, 
                        endpoints: Dict[str, str], description: str = "") -> bool:
        """Dynamically add a new MCP server"""
        self.servers[server_name] = {
            'name': server_name,
            'base_url': base_url,
            'endpoints': endpoints,
            'description': description
        }
        
        # Discover tools from the new server
        try:
            server = self.servers[server_name]
            tools = await self._get_server_tools(server)
            
            for tool in tools:
                self.tools[tool['name']] = tool
            
            logger.info(f"✅ Added server {server_name} with {len(tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add server {server_name}: {e}")
            del self.servers[server_name]
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the MCP tools manager"""
        return {
            "total_servers": len(self.servers),
            "total_tools": len(self.tools),
            "servers": list(self.servers.keys()),
            "tools_by_server": self.list_tools_by_server()
        }

# Global instance
mcp_manager = MCPToolsManager()

async def main():
    """Demo/test function"""
    print("🔧 MCP Tools Manager Demo")
    print("=" * 50)
    
    # Discover all tools
    tools_by_server = await mcp_manager.discover_tools()
    
    # Print statistics
    stats = mcp_manager.get_stats()
    print(f"📊 Total Servers: {stats['total_servers']}")
    print(f"🛠️ Total Tools: {stats['total_tools']}")
    print()
    
    # List tools by server
    for server_name, tools in stats['tools_by_server'].items():
        print(f"🏢 {server_name}:")
        for tool in tools:
            tool_info = mcp_manager.get_tool_info(tool)
            print(f"   • {tool}: {tool_info['description']}")
        print()
    
    # Check server health
    health = await mcp_manager.check_servers_health()
    print("🏥 Server Health:")
    for server, is_healthy in health.items():
        status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"   • {server}: {status}")

if __name__ == "__main__":
    asyncio.run(main())