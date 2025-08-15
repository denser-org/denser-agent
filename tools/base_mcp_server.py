#!/usr/bin/env python3
"""
Base MCP Server
Provides common functionality for all MCP servers to eliminate code duplication
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)


class BaseMCPServer:
    """Base class for all MCP servers with common functionality"""
    
    def __init__(self, name: str, port: int, tools: List[Dict[str, Any]] = None):
        self.name = name
        self.port = port
        self.tools = tools or []
        self.logger = logging.getLogger(f"{name}-mcp-server")
        
        # Create FastAPI app
        self.app = FastAPI(title=f"{name.title()} MCP Server", version="1.0.0")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup common routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup common FastAPI routes for MCP endpoints"""
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List available MCP tools"""
            return {"tools": self.tools}
        
        @self.app.post("/mcp/call_tool")
        async def call_tool(request: dict):
            """Call an MCP tool"""
            try:
                tool_name = request.get("name")
                arguments = request.get("arguments", {})
                
                if not tool_name:
                    raise HTTPException(status_code=400, detail="Tool name is required")
                
                # Execute the tool - implemented by subclasses
                result = await self.execute_tool(tool_name, arguments)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"❌ Tool call error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": f"{self.name}-mcp-server",
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_tool(self, name: str, arguments: dict) -> str:
        """Execute tool logic - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute_tool method")
    
    def start_server(self, tool_descriptions: List[str] = None):
        """Start the MCP server"""
        self.logger.info(f"🚀 Starting {self.name.title()} MCP Server...")
        self.logger.info(f"📡 Server will run on http://localhost:{self.port}")
        self.logger.info("🔧 MCP endpoints:")
        self.logger.info("   - GET  /mcp/tools - List available tools")
        self.logger.info("   - POST /mcp/call_tool - Call a tool")
        self.logger.info("   - GET  /health - Health check")
        
        if tool_descriptions:
            self.logger.info(f"🛠️ Available tools:")
            for desc in tool_descriptions:
                self.logger.info(f"   - {desc}")
        
        self.logger.info("=" * 60)
        
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)