#!/usr/bin/env python3
"""
Simplified Customer Support Agent Launcher
Directly runs the FastAPI-based customer support agent
"""

import subprocess
import sys
import os
import time
import signal
import asyncio
from typing import List

# Package imports (no sys.path needed after installation)

from tools.mcp_tools_manager import mcp_manager

class SimpleLauncher:
    """Simplified launcher for customer support agent"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.agent_dir = os.path.dirname(os.path.abspath(__file__))
    
    def start_mcp_servers(self):
        """Start required MCP servers"""
        servers_to_start = [
            ("../../tools/database/postgres/postgres_server.py", "Database"),
            ("../../tools/weather/weather_server.py", "Weather"), 
            ("../../tools/meeting/meeting_server.py", "Meeting")
        ]
        
        print("🚀 Starting MCP servers...")
        for server_path, server_name in servers_to_start:
            full_path = os.path.join(self.agent_dir, server_path)
            if os.path.exists(full_path):
                try:
                    process = subprocess.Popen(
                        [sys.executable, full_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.processes.append(process)
                    print(f"  ✅ {server_name} server started (PID: {process.pid})")
                except Exception as e:
                    print(f"  ❌ Failed to start {server_name} server: {e}")
            else:
                print(f"  ⚠️ {server_name} server not found at {server_path}")
        
        print("⏳ Waiting for servers to initialize...")
        time.sleep(3)
    
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ Stopped process {process.pid}")
            except:
                try:
                    process.kill()
                except:
                    pass
        print("🏁 All services stopped")
    
    def run(self):
        """Main run loop"""
        print("🎧 MCP Servers Launcher")
        print("=" * 60)
        
        # Setup signal handler
        def signal_handler(signum, frame):
            print("\n⚠️ Shutting down...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Check MCP connection
            try:
                health = asyncio.run(mcp_manager.check_servers_health())
                any_healthy = any(health.values())
                if not any_healthy:
                    print("🔌 No MCP servers detected, starting them...")
                    self.start_mcp_servers()
                else:
                    print("🔌 MCP servers already running")
            except:
                print("🔌 Starting MCP servers...")
                self.start_mcp_servers()
            
            print("\n🌟 MCP Servers are running!")
            print("=" * 40)
            print("🗄️ Database: http://localhost:8002")
            print("🌤️ Weather: http://localhost:8001")
            print("📅 Meeting: http://localhost:8004")
            print("\n💡 Next step: Start the main application with:")
            print("   cd /path/to/denser-agent")
            print("   python -m agents.customer_support.app")
            print("\n⏹️ Press Ctrl+C to stop MCP servers")
            
            # Keep servers running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.stop_all()
        
        return True

def main():
    """Main entry point"""
    launcher = SimpleLauncher()
    success = launcher.run()
    
    if success:
        print("\n🎉 MCP servers stopped successfully!")
    else:
        print("\n❌ MCP servers failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main()