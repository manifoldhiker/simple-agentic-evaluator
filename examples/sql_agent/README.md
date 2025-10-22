# SQL Agent Example

A simple SQL agent that converts natural language queries to SQL and executes them against a SQLite database.

## Overview

This example demonstrates:
- **Text-to-SQL conversion** using Claude
- **Safe SQL execution** with SQLite
- **Natural language responses** from query results
- **SAE framework integration** for testing

## Database Schema

The agent works with an e-commerce database:

**products table**
- id, name, category, price, stock, supplier
- 20 sample products across 4 categories (Electronics, Books, Clothing, Home)

**orders table**
- id, product_id, customer_name, quantity, order_date, status
- 30 sample orders over the last 90 days

## Files

- `db_setup.py` - Database creation and population
- `sql_agent.py` - Main agent implementation
- `run_sql_eval.py` - SAE wrapper and evaluation runner
- `create_test_cases.py` - Generates test cases Excel file
- `sql_agent_tests.xlsx` - 10 test cases for evaluation
- `SQL_AGENT_PLAN.md` - Design document

## Quick Start

### 1. Create Database

```bash
python db_setup.py
```

Creates `ecommerce.db` with sample data.

### 2. Test Agent Directly

```bash
python sql_agent.py
```

Runs a few test queries to verify the agent works.

### 3. Create Test Cases

```bash
python create_test_cases.py
```

Generates `sql_agent_tests.xlsx` with 10 test cases.

### 4. Run Evaluation

```bash
# Requires ANTHROPIC_API_KEY environment variable
python run_sql_eval.py
```

Runs full evaluation with SAE framework. Results in `sql_eval_results/`.

## Agent Capabilities

The SQL agent can handle:

✅ **Simple queries**: "How many products are there?"
✅ **Filtering**: "Show electronics under $100"
✅ **Aggregations**: "Total revenue from completed orders"
✅ **Joins**: "Show John's orders with product names"
✅ **Sorting**: "Top 3 most expensive products"
✅ **Error handling**: Graceful handling of no results

## Test Cases

10 test cases covering:
- **Simple queries** (2): Basic counts and status checks
- **Filtering** (3): Category, price, stock filters
- **Joins** (1): Orders with product details
- **Aggregation** (2): Counts, sums, distinct values
- **Sorting** (1): Top N queries
- **Edge cases** (1): No results handling

## Safety Features

The agent includes safety measures:
- ✅ Only allows SELECT queries
- ✅ Blocks DELETE, DROP, INSERT, UPDATE
- ✅ SQLite read-only operations
- ✅ Error handling for malformed SQL

## Architecture

```
User Query
    ↓
SQLAgent.query()
    ├─→ _generate_sql() - LLM converts NL to SQL
    ├─→ _execute_sql() - Run against SQLite
    └─→ _format_results() - Natural language response
```

## Example Interaction

```
Q: How many products are there in total?
A: Result: 20

Q: Show me all electronics products
A: Found 5 result(s):

1. id: 1, name: Laptop Pro 15, category: Electronics, price: 1299.99, stock: 15, supplier: TechCorp
2. id: 2, name: Smartphone X, category: Electronics, price: 799.99, stock: 25, supplier: TechCorp
...
```

## Evaluation with SAE

The `run_sql_eval.py` script:
1. Creates fresh test database
2. Initializes SQL Agent
3. Runs 10 test cases with EvaluatorAgent
4. Generates markdown reports for each test

Expected pass rate: 8-10 out of 10 tests

## Extending

To add more test cases:
1. Edit `create_test_cases.py`
2. Add new test dictionaries
3. Regenerate `sql_agent_tests.xlsx`
4. Run evaluation

To change the database:
1. Edit `db_setup.py` schema and data
2. Update `sql_agent.py` system prompt with new schema
3. Create appropriate test cases

## Implementation Notes

**Agent**: ~200 lines
**Database setup**: ~180 lines
**Wrapper**: ~50 lines
**Total**: ~430 lines

Uses:
- `anthropic` - For Claude API
- `sqlite3` - For database
- `pandas` - For Excel test cases

## Known Limitations

- Sequential execution only (no batch queries)
- No query optimization
- Basic error messages
- No query result caching
- Single-turn queries (no follow-ups using context)

These are intentional for v1 simplicity.
