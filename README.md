# Denser Agent

A multi-agent system built on MCP (Model Context Protocol) architecture providing specialized AI assistants with database analytics, weather information, and meeting scheduling capabilities.

## Quick Start

### Prerequisites

- Python 3.8+ with pip
- PostgreSQL (for database tools)
- Anthropic API key

```bash
pip install -r requirements.txt
pip install -e .
```

### Environment Setup

```bash
export CLAUDE_API_KEY="your-anthropic-api-key"
export OPENWEATHER_API_KEY="your-weather-api-key"  # Optional
```

### Database Setup

```bash
docker compose up -d postgres
cd tools/database/postgres && python setup_postgres.py
```

### Run Customer Support Agent

1. **Start MCP servers (Terminal 1):**
   ```bash
   cd agents/customer_support
   python start_servers.py
   ```
   This starts all required MCP servers (database, weather, meeting) and keeps them running. You'll see:
   ```
   🌟 MCP Servers are running!
   🗄️ Database: http://localhost:8002
   🌤️ Weather: http://localhost:8001
   📅 Meeting: http://localhost:8004
   ```
   **Keep this terminal open** - the servers run here.

2. **Start the main application (Terminal 2):**
   ```bash
   cd /path/to/denser-agent  # Project root
   python -m agents.customer_support.app
   ```
   This starts the FastAPI web interface on port 4000.

3. **Open your browser:** http://localhost:4000

## Available Tools

### Database Tools (Port 8002)
- **PostgreSQL integration** with sample data (customers, products, orders)
- **SQL query execution** with automatic chart generation
- **Analytics queries** optimized for visualization

```bash
cd tools/database/postgres
python postgres_server.py  # Start server
python postgres_demo.py    # Test operations
```

### Weather Tools (Port 8001)
- **Current weather** data for any location
- **Weather forecasts** with detailed conditions
- **Real or simulated data** (with/without API key)

```bash
cd tools/weather
python weather_server.py  # Start server
python weather_demo.py    # Test operations
```

### Meeting Tools (Port 8004)
- **Meeting scheduling** link generation
- **Calendar integration** via configurable URL
- **Simple booking** workflow

```bash
cd tools/meeting
python meeting_server.py  # Start server
python meeting_demo.py    # Test operations
```