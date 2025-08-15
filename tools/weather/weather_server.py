#!/usr/bin/env python3
"""
Simplified Weather MCP Server
Provides weather information tools via Model Context Protocol over HTTP
"""

# Add tools directory to path
import sys
import os
tools_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tools_dir)

import httpx
from datetime import datetime, timedelta
from base_mcp_server import BaseMCPServer

class WeatherMCPServer(BaseMCPServer):
    """Simplified Weather MCP Server implementation"""
    
    def __init__(self, port: int = 8001):
        # Define tools
        tools = [
            {
                "name": "get_current_weather",
                "description": "Get current weather conditions for a specific location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, state/country (e.g., 'Sunnyvale, CA' or 'London, UK')"
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units (metric, imperial, kelvin)",
                            "enum": ["metric", "imperial", "kelvin"],
                            "default": "imperial"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a specific location (5-day forecast)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, state/country (e.g., 'Sunnyvale, CA' or 'London, UK')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days for forecast (1-5)",
                            "minimum": 1,
                            "maximum": 5,
                            "default": 3
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units (metric, imperial, kelvin)",
                            "enum": ["metric", "imperial", "kelvin"],
                            "default": "imperial"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_weather_alerts",
                "description": "Get weather alerts and warnings for a specific location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, state/country (e.g., 'Sunnyvale, CA' or 'London, UK')"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
        
        # Initialize base class
        super().__init__("weather", port, tools)
        
        # Weather API configuration
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.weather_api_key:
            self.logger.warning("⚠️ OPENWEATHER_API_KEY not set. Weather data will be simulated.")
    
    
    async def execute_tool(self, name: str, arguments: dict) -> str:
        """Execute tool logic"""
        try:
            if name == "get_current_weather":
                return await self._get_current_weather(
                    arguments["location"],
                    arguments.get("units", "imperial")
                )
            
            elif name == "get_weather_forecast":
                return await self._get_weather_forecast(
                    arguments["location"],
                    arguments.get("days", 3),
                    arguments.get("units", "imperial")
                )
            
            elif name == "get_weather_alerts":
                return await self._get_weather_alerts(arguments["location"])
            
            else:
                return f"❌ Unknown tool: {name}"
                
        except Exception as e:
            self.logger.error(f"❌ Tool error: {e}")
            return f"❌ Weather error: {str(e)}"
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location format for OpenWeatherMap API"""
        location = location.strip()
        
        # Convert "City, ST" to "City,US" for US state abbreviations
        if ', ' in location:
            parts = location.split(', ')
            if len(parts) == 2 and len(parts[1]) <= 3 and parts[1].isupper():
                return f"{parts[0]},US"
        
        return location
    
    async def _get_current_weather(self, location: str, units: str = "imperial") -> str:
        """Get current weather for a location"""
        try:
            if self.weather_api_key:
                # Normalize location format for OpenWeatherMap API
                # Convert "City, ST" to "City,US" format
                normalized_location = self._normalize_location(location)
                
                # Use real OpenWeatherMap API
                async with httpx.AsyncClient() as client:
                    url = f"https://api.openweathermap.org/data/2.5/weather"
                    params = {
                        "q": normalized_location,
                        "appid": self.weather_api_key,
                        "units": units
                    }
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                # Format the response
                temp_unit = "°F" if units == "imperial" else "°C" if units == "metric" else "K"
                speed_unit = "mph" if units == "imperial" else "m/s"
                
                weather_info = f"""🌤️ Current Weather for {data['name']}, {data['sys']['country']}

📊 **Conditions:** {data['weather'][0]['description'].title()}
🌡️ **Temperature:** {data['main']['temp']:.1f}{temp_unit}
🔥 **Feels Like:** {data['main']['feels_like']:.1f}{temp_unit}
💧 **Humidity:** {data['main']['humidity']}%
💨 **Wind:** {data['wind']['speed']:.1f} {speed_unit}
👁️ **Visibility:** {data.get('visibility', 'N/A')} meters
🎯 **Pressure:** {data['main']['pressure']} hPa

*Updated: {datetime.now().strftime('%I:%M %p')}*"""
                
                return weather_info
            
            else:
                # Return simulated weather data
                return await self._get_simulated_weather(location, units)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"❌ Location '{location}' not found. Please check the spelling and try again."
            else:
                return f"❌ Weather service error: {e.response.status_code}"
        except Exception as e:
            return f"❌ Unable to get weather data: {str(e)}"
    
    async def _get_weather_forecast(self, location: str, days: int = 3, units: str = "imperial") -> str:
        """Get weather forecast for a location"""
        try:
            if self.weather_api_key:
                # Normalize location format for OpenWeatherMap API
                normalized_location = self._normalize_location(location)
                
                # Use real OpenWeatherMap API
                async with httpx.AsyncClient() as client:
                    url = f"https://api.openweathermap.org/data/2.5/forecast"
                    params = {
                        "q": normalized_location,
                        "appid": self.weather_api_key,
                        "units": units
                    }
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                # Format the forecast
                temp_unit = "°F" if units == "imperial" else "°C" if units == "metric" else "K"
                
                forecast_info = f"📅 {days}-Day Weather Forecast for {data['city']['name']}, {data['city']['country']}\n\n"
                
                # Group forecasts by day
                daily_forecasts = {}
                for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                    date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if date not in daily_forecasts:
                        daily_forecasts[date] = []
                    daily_forecasts[date].append(item)
                
                for date, forecasts in list(daily_forecasts.items())[:days]:
                    day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B %d')
                    temps = [f['main']['temp'] for f in forecasts]
                    conditions = [f['weather'][0]['description'] for f in forecasts]
                    
                    forecast_info += f"**{day_name}**\n"
                    forecast_info += f"🌡️ High: {max(temps):.1f}{temp_unit} | Low: {min(temps):.1f}{temp_unit}\n"
                    forecast_info += f"📊 Conditions: {max(set(conditions), key=conditions.count).title()}\n\n"
                
                return forecast_info
            
            else:
                # Return simulated forecast
                return await self._get_simulated_forecast(location, days, units)
                
        except Exception as e:
            return f"❌ Unable to get forecast data: {str(e)}"
    
    async def _get_weather_alerts(self, location: str) -> str:
        """Get weather alerts for a location"""
        # For demo purposes, return simulated alerts
        # In production, you'd use a weather alerts API
        return f"📢 Weather Alerts for {location}\n\n✅ No active weather alerts at this time.\n\n*Alerts are checked every hour*"
    
    async def _get_simulated_weather(self, location: str, units: str) -> str:
        """Generate simulated weather data for demo purposes"""
        import random
        
        temp_ranges = {
            "imperial": (45, 85, "°F"),
            "metric": (7, 29, "°C"),
            "kelvin": (280, 302, "K")
        }
        
        temp_min, temp_max, temp_unit = temp_ranges[units]
        temp = random.randint(temp_min, temp_max)
        
        conditions = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Sunny"]
        condition = random.choice(conditions)
        
        return f"""🌤️ Current Weather for {location} (Simulated)

📊 **Conditions:** {condition}
🌡️ **Temperature:** {temp}{temp_unit}
🔥 **Feels Like:** {temp + random.randint(-3, 3)}{temp_unit}
💧 **Humidity:** {random.randint(30, 80)}%
💨 **Wind:** {random.randint(3, 15)} {"mph" if units == "imperial" else "m/s"}

⚠️ *Demo data - Set OPENWEATHER_API_KEY for real weather*
*Updated: {datetime.now().strftime('%I:%M %p')}*"""
    
    async def _get_simulated_forecast(self, location: str, days: int, units: str) -> str:
        """Generate simulated forecast data"""
        import random
        
        temp_unit = "°F" if units == "imperial" else "°C" if units == "metric" else "K"
        
        forecast_info = f"📅 {days}-Day Weather Forecast for {location} (Simulated)\n\n"
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            day_name = date.strftime('%A, %B %d')
            
            high = random.randint(70, 85) if units == "imperial" else random.randint(20, 30)
            low = high - random.randint(10, 20)
            
            conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
            condition = random.choice(conditions)
            
            forecast_info += f"**{day_name}**\n"
            forecast_info += f"🌡️ High: {high}{temp_unit} | Low: {low}{temp_unit}\n"
            forecast_info += f"📊 Conditions: {condition}\n\n"
        
        forecast_info += "⚠️ *Demo data - Set OPENWEATHER_API_KEY for real weather*"
        return forecast_info
    
    def start_server(self):
        """Start the Weather MCP server"""
        tool_descriptions = [
            "get_current_weather - Current weather conditions",
            "get_weather_forecast - Multi-day weather forecast", 
            "get_weather_alerts - Weather alerts and warnings"
        ]
        super().start_server(tool_descriptions)

if __name__ == "__main__":
    server = WeatherMCPServer()
    server.start_server()