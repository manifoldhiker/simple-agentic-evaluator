"""Database setup for SQL Agent - creates and populates SQLite database."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def create_database(db_path: str = "ecommerce.db") -> None:
    """
    Create and populate SQLite database with sample e-commerce data.

    Args:
        db_path: Path to SQLite database file
    """
    # Remove existing database
    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            supplier TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            order_date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Insert products
    products = [
        # Electronics
        (1, "Laptop Pro 15", "Electronics", 1299.99, 15, "TechCorp"),
        (2, "Smartphone X", "Electronics", 799.99, 25, "TechCorp"),
        (3, "Wireless Headphones", "Electronics", 149.99, 50, "AudioMax"),
        (4, "USB-C Cable", "Electronics", 12.99, 100, "CablesCo"),
        (5, "Tablet 10-inch", "Electronics", 399.99, 20, "TechCorp"),

        # Books
        (6, "Python Programming", "Books", 45.99, 30, "BookWorld"),
        (7, "Science Fiction Novel", "Books", 14.99, 40, "BookWorld"),
        (8, "Cooking Mastery", "Books", 29.99, 25, "BookWorld"),
        (9, "History of Technology", "Books", 39.99, 15, "BookWorld"),

        # Clothing
        (10, "Cotton T-Shirt", "Clothing", 19.99, 60, "FashionHub"),
        (11, "Blue Jeans", "Clothing", 59.99, 35, "FashionHub"),
        (12, "Winter Jacket", "Clothing", 129.99, 12, "FashionHub"),
        (13, "Running Shoes", "Clothing", 89.99, 28, "SportsGear"),

        # Home
        (14, "LED Desk Lamp", "Home", 34.99, 45, "HomePlus"),
        (15, "Office Chair", "Home", 199.99, 8, "HomePlus"),
        (16, "Standing Desk", "Home", 449.99, 5, "HomePlus"),
        (17, "Coffee Maker", "Home", 79.99, 22, "KitchenPro"),
        (18, "Blender", "Home", 54.99, 18, "KitchenPro"),

        # More items
        (19, "Gaming Mouse", "Electronics", 49.99, 40, "TechCorp"),
        (20, "Yoga Mat", "Sports", 24.99, 55, "SportsGear"),
    ]

    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
        products
    )

    # Insert orders (last 90 days)
    today = datetime.now()
    orders = [
        (1, 2, "John Smith", 1, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "completed"),
        (2, 3, "John Smith", 2, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "completed"),
        (3, 10, "Jane Doe", 3, (today - timedelta(days=10)).strftime("%Y-%m-%d"), "shipped"),
        (4, 1, "Bob Wilson", 1, (today - timedelta(days=15)).strftime("%Y-%m-%d"), "completed"),
        (5, 7, "Alice Brown", 2, (today - timedelta(days=20)).strftime("%Y-%m-%d"), "completed"),
        (6, 15, "Charlie Davis", 1, (today - timedelta(days=25)).strftime("%Y-%m-%d"), "completed"),
        (7, 11, "Jane Doe", 2, (today - timedelta(days=30)).strftime("%Y-%m-%d"), "completed"),
        (8, 6, "David Miller", 1, (today - timedelta(days=2)).strftime("%Y-%m-%d"), "pending"),
        (9, 19, "John Smith", 1, (today - timedelta(days=3)).strftime("%Y-%m-%d"), "shipped"),
        (10, 14, "Emma Garcia", 2, (today - timedelta(days=8)).strftime("%Y-%m-%d"), "completed"),
        (11, 13, "Frank Martinez", 1, (today - timedelta(days=12)).strftime("%Y-%m-%d"), "shipped"),
        (12, 8, "Alice Brown", 1, (today - timedelta(days=18)).strftime("%Y-%m-%d"), "completed"),
        (13, 17, "Bob Wilson", 1, (today - timedelta(days=22)).strftime("%Y-%m-%d"), "completed"),
        (14, 12, "Grace Lee", 1, (today - timedelta(days=35)).strftime("%Y-%m-%d"), "completed"),
        (15, 5, "Henry Taylor", 1, (today - timedelta(days=40)).strftime("%Y-%m-%d"), "completed"),
        (16, 4, "Jane Doe", 5, (today - timedelta(days=45)).strftime("%Y-%m-%d"), "completed"),
        (17, 18, "Charlie Davis", 1, (today - timedelta(days=50)).strftime("%Y-%m-%d"), "completed"),
        (18, 20, "Emma Garcia", 2, (today - timedelta(days=55)).strftime("%Y-%m-%d"), "completed"),
        (19, 9, "David Miller", 1, (today - timedelta(days=60)).strftime("%Y-%m-%d"), "completed"),
        (20, 16, "Frank Martinez", 1, (today - timedelta(days=1)).strftime("%Y-%m-%d"), "pending"),
        (21, 2, "Alice Brown", 1, (today - timedelta(days=4)).strftime("%Y-%m-%d"), "shipped"),
        (22, 10, "Bob Wilson", 4, (today - timedelta(days=7)).strftime("%Y-%m-%d"), "completed"),
        (23, 7, "Grace Lee", 1, (today - timedelta(days=11)).strftime("%Y-%m-%d"), "completed"),
        (24, 3, "Henry Taylor", 1, (today - timedelta(days=14)).strftime("%Y-%m-%d"), "shipped"),
        (25, 11, "John Smith", 1, (today - timedelta(days=19)).strftime("%Y-%m-%d"), "completed"),
        (26, 15, "Emma Garcia", 1, (today - timedelta(days=28)).strftime("%Y-%m-%d"), "completed"),
        (27, 1, "Charlie Davis", 1, (today - timedelta(days=33)).strftime("%Y-%m-%d"), "completed"),
        (28, 13, "David Miller", 2, (today - timedelta(days=42)).strftime("%Y-%m-%d"), "completed"),
        (29, 6, "Jane Doe", 1, (today - timedelta(days=48)).strftime("%Y-%m-%d"), "completed"),
        (30, 19, "Frank Martinez", 1, (today - timedelta(days=65)).strftime("%Y-%m-%d"), "completed"),
    ]

    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        orders
    )

    conn.commit()
    conn.close()

    print(f"✓ Database created: {db_path}")
    print(f"  - {len(products)} products")
    print(f"  - {len(orders)} orders")


def get_schema_info(db_path: str = "ecommerce.db") -> str:
    """
    Get schema information as a formatted string for LLM context.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Formatted schema description
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table schemas
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schemas = cursor.fetchall()

    schema_text = "Database Schema:\n\n"
    for schema in schemas:
        schema_text += schema[0] + ";\n\n"

    # Get sample counts
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    schema_text += f"Total products: {product_count}\n"
    schema_text += f"Total orders: {order_count}\n"

    conn.close()

    return schema_text


if __name__ == "__main__":
    create_database()
    print("\nSchema:")
    print(get_schema_info())
