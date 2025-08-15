#!/usr/bin/env python3
"""
Weather MCP Demo Script
Demonstrates weather operations using the weather MCP server
"""

import requests
import json

WEATHER_MCP_URL = "http://localhost:8001"

def call_weather_tool(tool_name, arguments=None):
    """Helper function to call weather MCP tools"""
    if arguments is None:
        arguments = {}
    
    try:
        response = requests.post(
            f"{WEATHER_MCP_URL}/mcp/call_tool",
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

def demo_current_weather():
    """Test current weather for various locations"""
    print("🌤️ Current Weather Demo")
    print("=" * 40)
    
    locations = ["Sunnyvale, CA", "Beijing, China", "London, UK"]
    
    for location in locations:
        print(f"\n📍 {location}:")
        result = call_weather_tool("get_current_weather", {"location": location})
        print(result)

def demo_weather_forecast():
    """Test weather forecasts"""
    print("\n📅 Weather Forecast Demo")  
    print("=" * 40)
    
    print("\n📍 3-day forecast for Sunnyvale, CA:")
    result = call_weather_tool("get_weather_forecast", {
        "location": "Sunnyvale, CA",
        "days": 3
    })
    print(result)

def demo_weather_alerts():
    """Test weather alerts"""
    print("\n📢 Weather Alerts Demo")
    print("=" * 40)
    
    print("\n📍 Alerts for Sunnyvale, CA:")
    result = call_weather_tool("get_weather_alerts", {"location": "Sunnyvale, CA"})
    print(result)

def main():
    """Main demo function"""
    print("🎯 Weather MCP Server Demo")
    print("=" * 40)
    
    # Check server health
    try:
        response = requests.get(f"{WEATHER_MCP_URL}/health")
        if response.status_code != 200:
            print("❌ Weather MCP server not running")
            print("Start with: python weather_server.py")
            return
    except:
        print("❌ Cannot connect to Weather MCP server")
        print("Start with: python weather_server.py")
        return
    
    print("✅ Weather MCP server is running\n")
    
    # Run demos
    demo_current_weather()
    demo_weather_forecast()
    demo_weather_alerts()
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    main()