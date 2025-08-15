#!/usr/bin/env python3
"""
Setup Customer Analytics Demo Database
Creates sample tables and data to demonstrate generic database MCP usage
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import random
from datetime import datetime, timedelta
from faker import Faker

# Database configuration (same as other servers)
DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "product_database",
    "user": "product_admin", 
    "password": "product123",
    "port": 5432
}

fake = Faker()
random.seed(42)  # For reproducible data

def create_analytics_tables():
    """Create customer analytics tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            city VARCHAR(50),
            total_spent DECIMAL(10,2) DEFAULT 0.00
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price DECIMAL(8,2) NOT NULL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            order_total DECIMAL(10,2) NOT NULL,
            order_date DATE NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Analytics tables created successfully")

def insert_sample_data():
    """Insert sample data for demonstration"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM customers")
    
    # Insert sample customers
    customers_data = []
    for i in range(50):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
        city = fake.city()
        
        customers_data.append((
            first_name, last_name, email, city, 0.00
        ))
    
    cursor.executemany("""
        INSERT INTO customers (first_name, last_name, email, city, total_spent)
        VALUES (%s, %s, %s, %s, %s)
    """, customers_data)
    
    # Insert sample products
    products_data = [
        ('Laptop', 'Electronics', 899.99),
        ('Coffee Maker', 'Appliances', 89.99),
        ('Running Shoes', 'Footwear', 159.99),
        ('Smartphone', 'Electronics', 699.99),
        ('Desk Chair', 'Furniture', 299.99),
        ('Bluetooth Speaker', 'Electronics', 79.99),
        ('Water Bottle', 'Accessories', 24.99),
        ('Book', 'Education', 19.99),
        ('Headphones', 'Electronics', 129.99),
        ('Backpack', 'Accessories', 69.99)
    ]
    
    cursor.executemany("""
        INSERT INTO products (product_name, category, price)
        VALUES (%s, %s, %s)
    """, products_data)
    
    # Insert sample orders
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall()
    
    orders_data = []
    
    for i in range(200):  # 200 orders
        customer_id = random.choice(customer_ids)
        product_id, price = random.choice(products)
        quantity = random.randint(1, 3)
        order_total = round(float(price) * quantity, 2)
        order_date = fake.date_between(start_date='-1y', end_date='today')
        
        orders_data.append((
            customer_id, product_id, quantity, order_total, order_date
        ))
    
    cursor.executemany("""
        INSERT INTO orders (customer_id, product_id, quantity, order_total, order_date)
        VALUES (%s, %s, %s, %s, %s)
    """, orders_data)
    
    # Update customer total_spent
    cursor.execute("""
        UPDATE customers 
        SET total_spent = (
            SELECT COALESCE(SUM(order_total), 0) 
            FROM orders 
            WHERE orders.customer_id = customers.customer_id
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Sample data inserted successfully")
    print(f"   • 50 customers")
    print(f"   • 10 products")
    print(f"   • 200 orders")

def main():
    """Main setup function"""
    print("🗄️ Setting up Customer Analytics Demo Database")
    print("=" * 50)
    
    try:
        create_analytics_tables()
        insert_sample_data()
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    main()