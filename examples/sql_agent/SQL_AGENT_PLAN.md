# SQL Agent Design Plan

## Overview

A simple SQL agent that converts natural language queries to SQL, executes them against a SQLite database, and returns results in natural language.

## Database Design

**Domain**: E-commerce product inventory

### Schema

**products table**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    supplier TEXT NOT NULL
);
```

**orders table**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    order_date DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Sample Data

**Products** (20 items across categories: Electronics, Books, Clothing, Home)
- Laptop, Phone, Headphones (Electronics)
- Novel, Cookbook, Technical Manual (Books)
- T-Shirt, Jeans, Jacket (Clothing)
- Lamp, Chair, Desk (Home)

**Orders** (30 orders with various dates, customers, statuses)
- Mix of completed, pending, shipped orders
- Date range: last 3 months
- 5-6 different customers

## Agent Architecture

```
User Query
    ↓
SQL Agent
    ├─→ LLM (Claude) converts query to SQL
    ├─→ Execute SQL on SQLite DB
    ├─→ Format results
    └─→ Return natural language response
```

## Agent Capabilities

1. **Simple Queries**
   - "Show all products"
   - "What electronics do we have?"
   - "How many products in stock?"

2. **Filtering & Search**
   - "Find products under $50"
   - "Show products from SupplierX"
   - "What's in the Electronics category?"

3. **Aggregations**
   - "Total revenue from completed orders"
   - "Average product price by category"
   - "Top 3 selling products"

4. **Joins**
   - "Show orders for customer John"
   - "What products have been ordered?"
   - "Orders with product details"

5. **Error Handling**
   - Invalid queries → helpful error message
   - No results → "No matching records found"
   - SQL errors → graceful degradation

## Agent Implementation

**Class**: `SQLAgent`

**Methods**:
- `__init__(db_path)`: Initialize with SQLite database
- `query(user_message)`: Main interface - takes natural language, returns answer
- `_generate_sql(question)`: LLM call to convert NL to SQL
- `_execute_sql(sql)`: Execute SQL safely
- `_format_results(results)`: Convert results to natural language
- `reset_conversation()`: Clear chat history

**State**:
- Database connection
- Conversation history (for multi-turn queries)
- Schema information (for LLM context)

## SAE Wrapper

**Class**: `SQLAgentWrapper(AUTWrapper)`

**Setup**:
- Create fresh SQLite DB for each test run
- Populate with known data
- Initialize SQLAgent

**Methods**:
- `invoke()`: Call agent.query()
- `reset()`: Reset conversation history (keep DB)

## Test Cases

Create `sql_agent_tests.xlsx` with ~10 test cases:

1. **basic_query**: "List all products" → Should return multiple products
2. **category_filter**: "Show electronics" → Returns only electronics
3. **price_filter**: "Products under $50" → Correct filtering
4. **aggregation**: "How many products total?" → Correct count
5. **join_query**: "Show John's orders" → Orders with product names
6. **no_results**: "Find products from FakeSupplier" → Graceful handling
7. **stock_check**: "What's low on stock?" → Products with stock < 10
8. **revenue**: "Total completed order value" → Correct calculation
9. **multi_turn**: Ask count, then details → Maintains context
10. **invalid_query**: "Delete all products" → Refuses or errors safely

## Success Criteria

- Agent correctly interprets 8/10 queries
- No SQL injection vulnerabilities
- Graceful error handling
- Results are accurate against known DB state
- Multi-turn conversations work

## Implementation Steps

1. Create `examples/sql_agent/` directory
2. Write `db_setup.py` - creates and populates SQLite DB
3. Write `sql_agent.py` - main agent implementation
4. Write `sql_agent_wrapper.py` - SAE wrapper
5. Create `sql_agent_tests.xlsx` - test cases
6. Run evaluation with SAE framework

---

**Target**: ~200 lines for agent, ~50 lines for DB setup, ~50 lines for wrapper
