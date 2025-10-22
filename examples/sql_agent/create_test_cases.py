"""Create test cases for SQL Agent evaluation."""

import pandas as pd
from pathlib import Path


def create_test_cases():
    """Create SQL Agent test cases Excel file."""

    test_cases = [
        {
            "test_name": "basic_count",
            "query": "How many products are there in total?",
            "expected_behavior": "Returns count of 20 products",
            "verification": "Should execute COUNT query and return 20",
            "category": "simple"
        },
        {
            "test_name": "category_filter",
            "query": "Show me all electronics products",
            "expected_behavior": "Returns only products in Electronics category",
            "verification": "Should filter by category='Electronics', return 5 items",
            "category": "filtering"
        },
        {
            "test_name": "price_filter",
            "query": "What products cost less than $50?",
            "expected_behavior": "Returns products with price < 50",
            "verification": "Should filter by price, multiple results expected",
            "category": "filtering"
        },
        {
            "test_name": "join_query",
            "query": "Show me all orders by John Smith with product names",
            "expected_behavior": "Returns orders joined with product details",
            "verification": "Should JOIN orders and products tables, filter by customer_name",
            "category": "joins"
        },
        {
            "test_name": "aggregation",
            "query": "What's the total value of all completed orders?",
            "expected_behavior": "Calculates SUM(price * quantity) for completed orders",
            "verification": "Should aggregate order values, join with products",
            "category": "aggregation"
        },
        {
            "test_name": "no_results",
            "query": "Find products from supplier 'NonExistentCorp'",
            "expected_behavior": "Returns empty result gracefully",
            "verification": "Should handle no results case with clear message",
            "category": "edge_cases"
        },
        {
            "test_name": "low_stock",
            "query": "Which products have less than 10 items in stock?",
            "expected_behavior": "Returns products with stock < 10",
            "verification": "Should filter by stock level",
            "category": "filtering"
        },
        {
            "test_name": "order_status",
            "query": "How many orders are still pending?",
            "expected_behavior": "Counts orders with status='pending'",
            "verification": "Should filter and count pending orders",
            "category": "simple"
        },
        {
            "test_name": "top_products",
            "query": "What are the 3 most expensive products?",
            "expected_behavior": "Returns top 3 products ordered by price DESC",
            "verification": "Should ORDER BY price DESC LIMIT 3",
            "category": "sorting"
        },
        {
            "test_name": "category_count",
            "query": "How many different product categories are there?",
            "expected_behavior": "Counts distinct categories",
            "verification": "Should use COUNT(DISTINCT category)",
            "category": "aggregation"
        }
    ]

    # Create DataFrame
    df = pd.DataFrame(test_cases)

    # Save to Excel
    output_path = Path(__file__).parent / "sql_agent_tests.xlsx"
    df.to_excel(output_path, index=False)

    print(f"✓ Created test cases: {output_path}")
    print(f"  Total test cases: {len(test_cases)}")
    print("\nTest case breakdown by category:")

    # Show breakdown
    category_counts = df.groupby("category").size()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")

    print("\nTest cases:")
    for i, tc in enumerate(test_cases, 1):
        print(f"  {i}. {tc['test_name']}: {tc['query']}")


if __name__ == "__main__":
    create_test_cases()
