#!/usr/bin/env python3
"""
Simplified Base Agent Classes
FastAPI-based shared functionality for all Denser Agent types
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import time
import uvicorn
from typing import Dict, List, Any
from abc import ABC, abstractmethod

from tools.mcp_tools_manager import mcp_manager


# Pydantic models
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]


class ConfigResponse(BaseModel):
    agent_name: str
    agent_type: str
    agent_emoji: str
    agent_description: str
    primary_color: str
    background_gradient: str
    initial_message: str
    input_placeholder: str


class BaseAgentApp(ABC):
    """Simplified FastAPI app for agents"""

    def __init__(self, agent_type: str, agent_dir: str):
        self.agent_type = agent_type
        self.agent_dir = agent_dir
        self.config = self._load_config()
        self.app = FastAPI(title=f"{agent_type.title()} Agent", version="1.0.0")

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.setup_routes()

    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        try:
            config_path = os.path.join(self.agent_dir, 'config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return {}

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def serve_index():
            """Serve the shared chatbot HTML file"""
            agents_dir = os.path.dirname(self.agent_dir)
            chatbot_path = os.path.join(agents_dir, 'chatbot.html')
            return FileResponse(chatbot_path)

        @self.app.get("/api/config", response_model=ConfigResponse)
        async def get_config():
            """Get agent configuration for UI customization"""
            try:
                return ConfigResponse(
                    agent_name=self.config.get('agent_name', f"{self.agent_type.title()} Assistant"),
                    agent_type=self.agent_type,
                    agent_emoji=self.get_agent_emoji(),
                    agent_description=self.get_agent_description(),
                    primary_color=self.get_primary_color(),
                    background_gradient=self.get_background_gradient(),
                    initial_message=self.get_initial_message(),
                    input_placeholder=self.get_input_placeholder()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/chat")
        async def chat_endpoint(request: ChatRequest):
            """Handle chat messages using LLM with MCP tool calling"""
            try:
                messages = request.messages

                if not messages:
                    raise HTTPException(status_code=400, detail="No messages provided")

                # Check MCP server health
                health_status = await mcp_manager.check_servers_health()
                if not any(health_status.values()):
                    raise HTTPException(status_code=500, detail="MCP servers unavailable")

                # Handle chat with tools
                response = await self.handle_chat_with_tools(messages)
                return response

            except Exception as e:
                print(f"Chat error: {e}")
                raise HTTPException(status_code=500, detail="Sorry, I encountered an error.")

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                health_status = await mcp_manager.check_servers_health()
                return {
                    'status': 'healthy',
                    'mcp_servers': health_status,
                    'timestamp': time.time()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    @abstractmethod
    async def handle_chat_with_tools(self, messages):
        """Handle chat with agent-specific logic"""
        pass

    def get_agent_emoji(self):
        """Get agent emoji for UI"""
        emoji_map = {
            'customer_support': '🎧',
            'default': '🤖'
        }
        return emoji_map.get(self.agent_type, emoji_map['default'])

    def get_agent_description(self):
        """Get agent description for UI"""
        descriptions = {
            'customer_support': 'Database queries, technical support, and meeting scheduling'
        }
        return descriptions.get(self.agent_type, 'How can I help you today?')

    def get_primary_color(self):
        """Get primary color for UI theme"""
        colors = {
            'customer_support': '#6c5ce7'
        }
        return colors.get(self.agent_type, '#4F7DF3')

    def get_background_gradient(self):
        """Get background gradient for UI"""
        gradients = {
            'customer_support': 'linear-gradient(135deg, #6c5ce7 0%, #5a4fcf 100%)'
        }
        return gradients.get(self.agent_type, 'linear-gradient(135deg, #4F7DF3 0%, #3d6bcc 100%)')

    def get_initial_message(self):
        """Get initial message for chat"""
        if self.agent_type == 'customer_support':
            return '''Hello! I'm your customer support assistant. I can help with database queries, technical support, and scheduling meetings.
                        <div class="quick-buttons">
                            <div class="quick-btn" onclick="sendQuickMessage('Show me database analytics')">Database Analytics</div>
                            <div class="quick-btn" onclick="sendQuickMessage('Schedule a meeting')">Schedule Meeting</div>
                        </div>'''
        return 'Welcome! How can I help you today?'

    def get_input_placeholder(self):
        """Get input placeholder text"""
        placeholders = {
            'customer_support': 'Ask about database queries, technical issues, meetings...'
        }
        return placeholders.get(self.agent_type, 'Ask me anything...')

    def run(self, host='0.0.0.0', port=4000, reload=True):
        """Run the FastAPI app with uvicorn"""
        uvicorn.run(self.app, host=host, port=port, reload=reload)


# MCP tool helper functions
async def call_mcp_tool(tool_name: str, arguments: dict):
    """Call MCP tool via Tools Manager"""
    try:
        result = await mcp_manager.call_tool(tool_name, arguments)
        return result
    except Exception as e:
        print(f"❌ MCP tool call error: {e}")
        return f"❌ Error calling {tool_name}: {str(e)}"


async def get_mcp_tools():
    """Get available tools from all MCP servers"""
    try:
        tools = await mcp_manager.get_all_tools_for_llm()
        return tools
    except Exception as e:
        print(f"❌ Failed to get MCP tools: {e}")
        return []
