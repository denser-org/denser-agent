# Weather Tools Setup Guide

This guide covers setting up the Weather MCP server for the Denser Agent project.

## Prerequisites

- Python 3.8+ with pip
- Required Python packages: `fastapi`, `uvicorn`, `httpx`
- Optional: OpenWeatherMap API key for real weather data

```bash
pip install fastapi uvicorn httpx
```

## OpenWeatherMap API Setup (Optional)

**1. Get API key:**
- Sign up at [openweathermap.org](https://openweathermap.org/api)
- Get your free API key

**2. Set environment variable:**
```bash
# Add to ~/.zshrc or ~/.bash_profile
export OPENWEATHER_API_KEY="your-api-key-here"
```

**Note:** Without an API key, the server will provide simulated weather data for demo purposes.

## Running the Weather Server

**1. Start the weather MCP server:**
```bash
cd tools/weather
python weather_server.py
```

The server runs on `http://localhost:8001` with these endpoints:
- `GET /health` - Health check
- `GET /mcp/tools` - List available tools
- `POST /mcp/call_tool` - Execute weather operations

**2. Test the weather server:**
```bash
# In another terminal
python weather_demo.py
```
