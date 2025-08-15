#!/usr/bin/env python3
"""
Simplified Meeting MCP Server
Provides meeting scheduling tools via Model Context Protocol over HTTP
"""

# Add tools directory to path
import sys
import os

tools_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tools_dir)

from base_mcp_server import BaseMCPServer


class MeetingMCPServer(BaseMCPServer):
    """Simplified Meeting MCP Server implementation"""

    def __init__(self, meeting_url: str, port: int = 8004):
        # Define tools
        tools = [
            {
                "name": "schedule_meeting",
                "description": "Generate a meeting scheduling link for the user",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

        # Initialize base class
        super().__init__("meeting", port, tools)

        self.meeting_url = meeting_url

    async def execute_tool(self, name: str, arguments: dict) -> str:
        """Execute tool logic"""
        try:
            if name == "schedule_meeting":
                return await self._schedule_meeting()
            else:
                return f"❌ Unknown tool: {name}"

        except Exception as e:
            self.logger.error(f"❌ Tool error: {e}")
            return f"❌ Meeting error: {str(e)}"

    async def _schedule_meeting(self) -> str:
        """Generate meeting scheduling response"""
        return f"""I'd be happy to help you schedule a meeting!

👉 [**Schedule Meeting**]({self.meeting_url})"""

    def start_server(self):
        """Start the Meeting MCP server"""
        self.logger.info(f"🔗 Meeting URL: {self.meeting_url}")
        tool_descriptions = [
            "schedule_meeting - Generate meeting scheduling link"
        ]
        super().start_server(tool_descriptions)


if __name__ == "__main__":
    # Example meeting URL - replace with actual URL
    meeting_url = "https://calendly.com/YOUR_MEETING_URL"
    server = MeetingMCPServer(meeting_url)
    server.start_server()
