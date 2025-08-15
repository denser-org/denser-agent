#!/usr/bin/env python3
"""
Database MCP Demo Script
Demonstrates various database operations using the generic database MCP server
"""

import requests
import json
import time

DATABASE_MCP_URL = "http://localhost:8002"

def call_database_tool(tool_name, arguments=None):
    """Helper function to call database MCP tools"""
    if arguments is None:
        arguments = {}
    
    try:
        response = requests.post(
            f"{DATABASE_MCP_URL}/mcp/call_tool",
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

def demo_basic_operations():
    """Demonstrate basic database operations"""
    print("🗄️ Database MCP Demo - Basic Operations")
    print("=" * 50)
    
    # List all tables
    print("\n1️⃣ List all tables:")
    result = call_database_tool("list_tables")
    print(result)
    
    # Describe customers table
    print("\n2️⃣ Describe customers table:")
    result = call_database_tool("describe_table", {"table_name": "customers"})
    print(result)
    
    # Get sample customer data
    print("\n3️⃣ Sample customer data:")
    result = call_database_tool("get_table_data", {"table_name": "customers", "limit": 5})
    print(result)

def demo_analytics_queries():
    """Demonstrate analytics queries"""
    print("\n\n📊 Database MCP Demo - Analytics Queries")
    print("=" * 50)
    
    # Top customers by spending
    print("\n1️⃣ Top 5 customers by total spent:")
    query = """
    SELECT first_name, last_name, total_spent 
    FROM customers 
    ORDER BY total_spent DESC 
    LIMIT 5
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)
    
    # Monthly sales summary
    print("\n2️⃣ Monthly sales summary:")
    query = """
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        COUNT(*) as total_orders,
        SUM(order_total) as total_revenue
    FROM orders 
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY month DESC
    LIMIT 6
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)
    
    # Sales by product category
    print("\n3️⃣ Sales by product category:")
    query = """
    SELECT 
        p.category,
        COUNT(*) as order_count,
        SUM(o.order_total) as total_revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)

def demo_product_analysis():
    """Demonstrate product analysis"""
    print("\n\n📦 Database MCP Demo - Product Analysis")
    print("=" * 50)
    
    # All products
    print("\n1️⃣ All products:")
    result = call_database_tool("get_table_data", {"table_name": "products", "limit": 10})
    print(result)
    
    # Best selling products
    print("\n2️⃣ Most ordered products:")
    query = """
    SELECT 
        p.product_name,
        p.category,
        p.price,
        SUM(o.quantity) as total_sold
    FROM products p
    JOIN orders o ON p.product_id = o.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.price
    ORDER BY total_sold DESC
    LIMIT 5
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)

def demo_simple_queries():
    """Demonstrate simple queries for chart testing"""
    print("\n\n🔍 Database MCP Demo - Chart-Ready Queries")
    print("=" * 50)
    
    # Customer spending (good for pie chart)
    print("\n1️⃣ Top customers spending (pie chart data):")
    query = """
    SELECT first_name || ' ' || last_name as customer_name, total_spent
    FROM customers 
    WHERE total_spent > 0
    ORDER BY total_spent DESC
    LIMIT 5
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)
    
    # Orders by month (good for line chart)
    print("\n2️⃣ Orders by month (line chart data):")
    query = """
    SELECT 
        TO_CHAR(order_date, 'YYYY-MM') as month,
        COUNT(*) as order_count
    FROM orders 
    GROUP BY TO_CHAR(order_date, 'YYYY-MM')
    ORDER BY month
    LIMIT 6
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)
    
    # Category sales (good for bar chart)
    print("\n3️⃣ Sales by category (bar chart data):")
    query = """
    SELECT 
        p.category,
        SUM(o.order_total) as total_sales
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_sales DESC
    """
    result = call_database_tool("execute_query", {"query": query})
    print(result)

def main():
    """Main demo function"""
    print("🎯 Generic Database MCP Server Demo")
    print("Using Customer Analytics Database")
    print("=" * 60)
    
    # Check if database server is running
    try:
        response = requests.get(f"{DATABASE_MCP_URL}/health")
        if response.status_code != 200:
            print("❌ Database MCP server is not running")
            print("Please start it with: python database_server.py")
            return
    except:
        print("❌ Cannot connect to Database MCP server")
        print("Please start it with: python database_server.py")
        return
    
    print("✅ Database MCP server is running\n")
    
    # Run demos
    demo_basic_operations()
    demo_analytics_queries()
    demo_product_analysis()
    demo_simple_queries()
    
    print("\n\n🎉 Demo completed!")

if __name__ == "__main__":
    main()