# Meeting Tools Setup Guide

This guide covers setting up the Meeting MCP server for the Denser Agent project.

## Prerequisites

- Python 3.8+ with pip
- Required Python packages: `fastapi`, `uvicorn`

```bash
pip install fastapi uvicorn
```

## Running the Meeting Server

**1. Start the meeting MCP server:**
```bash
cd tools/meeting
python meeting_server.py
```

The server runs on `http://localhost:8004` with these endpoints:
- `GET /health` - Health check
- `GET /mcp/tools` - List available tools
- `POST /mcp/call_tool` - Execute meeting operations

**2. Test the meeting server:**
```bash
# In another terminal
python meeting_demo.py
```

## Available Meeting Tools

### schedule_meeting
Generate a meeting scheduling link for the user.

**Parameters:** None (meeting URL is configured in server initialization)

**Returns:** Formatted message with meeting scheduling link

## Configuration

The meeting URL is set in the server initialization. Edit `meeting_server.py` to change the default URL:

```python
# Example meeting URL - replace with actual URL
meeting_url = "https://calendly.com/your-username/30min"
server = MeetingMCPServer(meeting_url)
```

## Demo Features

The `meeting_demo.py` script demonstrates:
- Simple meeting scheduling link generation
- Server health checking
- Basic error handling