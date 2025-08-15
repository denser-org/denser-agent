#!/usr/bin/env python3
"""
Meeting MCP Demo Script
Demonstrates meeting scheduling using the meeting MCP server
"""

import requests
import json

MEETING_MCP_URL = "http://localhost:8004"

def call_meeting_tool(tool_name, arguments=None):
    """Helper function to call meeting MCP tools"""
    if arguments is None:
        arguments = {}
    
    try:
        response = requests.post(
            f"{MEETING_MCP_URL}/mcp/call_tool",
            json={"name": tool_name, "arguments": arguments},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"]
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Connection error: {str(e)}"

def demo_schedule_meeting():
    """Test meeting scheduling"""
    print("📅 Meeting Scheduling Demo")
    print("=" * 40)
    
    print("\n📍 Schedule meeting:")
    result = call_meeting_tool("schedule_meeting")
    print(result)

def main():
    """Main demo function"""
    print("🎯 Meeting MCP Server Demo")
    print("=" * 40)
    
    # Check server health
    try:
        response = requests.get(f"{MEETING_MCP_URL}/health")
        if response.status_code != 200:
            print("❌ Meeting MCP server not running")
            print("Start with: python meeting_server.py")
            return
    except:
        print("❌ Cannot connect to Meeting MCP server")
        print("Start with: python meeting_server.py")
        return
    
    print("✅ Meeting MCP server is running\n")
    
    # Run demo
    demo_schedule_meeting()
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    main()