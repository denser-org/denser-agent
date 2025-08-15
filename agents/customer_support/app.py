#!/usr/bin/env python3
"""
Simplified Customer Support Agent
FastAPI-based customer support chatbot with database and tool capabilities
"""

import os
from typing import Dict, Any

# Package imports (no sys.path needed after installation)
from agents.base_agent import BaseAgentApp, call_mcp_tool, get_mcp_tools
from agents.chart_utils import generate_chart_data
from tools.mcp_tools_manager import mcp_manager


def extract_table_names_simple(text):
    lines = text.split('\n')
    tables = []
    for line in lines:
        if '**' in line and any(char.isdigit() for char in line):
            # Extract text between ** markers
            start = line.find('**') + 2
            end = line.rfind('**')
            if start < end:
                tables.append(line[start:end])
    return tables

class CustomerSupportAgentApp(BaseAgentApp):
    """Simplified Customer Support agent application"""

    def __init__(self):
        agent_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__("customer_support", agent_dir)
        self.table_schemas = {}
        self.schemas_cached = False

    async def _get_table_schemas(self):
        """Get and cache table schemas"""
        if self.schemas_cached:
            return self.table_schemas

        try:
            await mcp_manager.discover_tools()
            tables_result = await call_mcp_tool('list_tables', {})
            # '## 📋 Database Tables\n\n1. **customers**\n2. **orders**\n3. **products**\n'
            tables = extract_table_names_simple(tables_result)
            for table in tables:
                try:
                    schema = await call_mcp_tool('describe_table', {'table_name': table})
                    if schema:
                        self.table_schemas[table] = schema
                except Exception:
                    continue

            self.schemas_cached = True
            return self.table_schemas

        except Exception as e:
            print(f"❌ Schema initialization failed: {e}")
            return {}

    async def handle_chat_with_tools(self, messages) -> Dict[str, Any]:
        """Simplified LLM chat handling with tool calling"""
        try:
            # Get table schemas and limit messages
            await self._get_table_schemas()

            max_turns = self.config.get('components', {}).get('memory', {}).get('session_memory', {}).get('max_turns',
                                                                                                          5)
            if len(messages) > max_turns:
                messages = messages[-max_turns:]

            # Initialize Claude client
            from anthropic import Anthropic
            api_key = os.getenv('CLAUDE_API_KEY')
            if not api_key:
                return {'success': False, 'message': 'Claude API key not configured'}

            client = Anthropic(api_key=api_key)

            # Get available tools
            await mcp_manager.discover_tools()
            available_tools = await get_mcp_tools()

            # Build system prompt
            tool_names = [t['name'] for t in available_tools]
            # Build comprehensive system prompt with all tool context
            schema_context = ""
            if self.table_schemas:
                schema_context = "\n\nDatabase Schema:\n"
                for table_name, schema in self.table_schemas.items():
                    schema_context += f"\nTable: {table_name}\n{schema}\n"

            # schema_info = "\n".join([f"Table: {name}" for name in self.table_schemas.keys()]) if self.table_schemas else ""

            system_prompt = f"""You are a customer support assistant with access to tools. ALWAYS use the appropriate tool for user requests.

Available tools: {tool_names}{schema_context}

IMPORTANT: 
- For weather questions (current weather, forecasts, alerts) → use get_current_weather, get_weather_forecast, or get_weather_alerts
- For database queries (customer data, analytics, reports) → use execute_query, describe_table, list_tables, or get_table_data  
- For meeting requests → use schedule_meeting

When a user asks about weather, database data, or meetings, you MUST call the appropriate tool. Do not just explain what you would do - actually use the tools."""

            # Prepare tools for Claude
            claude_tools = []
            for tool in available_tools:
                claude_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["input_schema"]
                })

            print(f"🔧 Available tools: {[t['name'] for t in claude_tools]}")

            # Call LLM with tools
            llm_config = self.config.get('components', {}).get('llm', {})
            response = client.messages.create(
                model=llm_config.get('model', 'claude-3-5-haiku-latest'),
                max_tokens=llm_config.get('max_tokens', 1000),
                system=system_prompt,
                messages=messages,
                tools=claude_tools
            )

            # Debug: Show what Claude responded with
            print(f"🔍 Claude response content types: {[c.type for c in response.content]}")
            for i, content in enumerate(response.content):
                print(f"🔍 Content {i}: type={content.type}")
                if hasattr(content, 'text'):
                    print(f"🔍 Text: {content.text[:100]}...")
                if hasattr(content, 'name'):
                    print(f"🔍 Tool: {content.name}")

            # Handle tool use or text response - prioritize tool_use
            tool_use_content = None
            text_content = None

            for content in response.content:
                if content.type == "tool_use":
                    tool_use_content = content
                elif content.type == "text":
                    text_content = content

            # Process tool_use first if present
            if tool_use_content:
                print(f"🛠️ Calling tool: {tool_use_content.name}")
                # Decide whether to use tool, and how to use tool, ie, parameters
                print(f"Tool Name: {tool_use_content.name}")
                print(f"Tool Input: {tool_use_content.input}")
                tool_result = await call_mcp_tool(tool_use_content.name, tool_use_content.input)
                if tool_result:
                    # Create reasoning step
                    tool_type = 'Database' if tool_use_content.name.startswith(
                        ('execute_', 'describe_', 'list_', 'get_table')) else 'Tool'
                    reasoning_step = {
                        'type': 'tool',
                        'header': f'{tool_type} Operation',
                        'content': f'**Tool:** {tool_use_content.name}\n**Args:** {tool_use_content.input}'
                    }

                    # Generate chart for database results
                    chart_data = None
                    if tool_use_content.name in ['execute_query', 'get_table_data']:
                        chart_data = generate_chart_data(tool_result)

                    response_data = {
                        'success': True,
                        'message': tool_result,
                        'reasoning_step': reasoning_step
                    }

                    if chart_data:
                        response_data['chart_data'] = chart_data

                    return response_data

            # Fall back to text if no tool_use
            elif text_content:
                print(f"📝 Claude returned text response: {text_content.text[:100]}...")
                return {'success': True, 'message': text_content.text}

            return {'success': True,
                    'message': 'Hello! I can help with database queries, weather, and meeting scheduling.'}

        except Exception as e:
            print(f"❌ Chat error: {e}")
            return {'success': False, 'message': 'Sorry, I encountered an error. Please try again.'}


def main():
    """Main entry point function"""
    import asyncio

    print("🎧 Starting Customer Support Assistant...")
    print("📡 FastAPI server will run on http://localhost:4000")
    print("🌐 Customer Support UI available at http://localhost:4000")

    # Check MCP servers
    try:
        health_status = asyncio.run(mcp_manager.check_servers_health())
        print("🔌 MCP Servers:")
        for server_name, is_healthy in health_status.items():
            status = "✅" if is_healthy else "❌"
            print(f"   {status} {server_name}")
    except Exception as e:
        print(f"🔌 MCP connection error: {e}")

    print("=" * 60)

    # Run the FastAPI app
    app = CustomerSupportAgentApp()
    app.run(host='0.0.0.0', port=4000, reload=False)


if __name__ == '__main__':
    main()
