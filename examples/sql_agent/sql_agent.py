"""SQL Agent - converts natural language to SQL queries."""

import sqlite3
from typing import Optional
import anthropic
from db_setup import get_schema_info


class SQLAgent:
    """
    Agent that converts natural language queries to SQL and executes them.

    Uses Claude to translate user questions into SQL, executes safely,
    and formats results in natural language.
    """

    def __init__(
        self,
        db_path: str = "ecommerce.db",
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize SQL Agent.

        Args:
            db_path: Path to SQLite database
            model: Anthropic model to use
        """
        self.db_path = db_path
        self.model = model
        self.client = anthropic.Anthropic()
        self.conversation_history = []

        # Get schema for LLM context
        self.schema_info = get_schema_info(db_path)

        # System prompt for SQL generation
        self.system_prompt = f"""You are a SQL assistant. Convert natural language questions to SQL queries.

{self.schema_info}

Guidelines:
1. Generate valid SQLite queries only
2. Use SELECT statements (no DELETE, DROP, or other destructive operations)
3. Join tables when needed to provide complete information
4. Format results clearly
5. If the question is unclear, ask for clarification
6. If no results are found, say so clearly

When generating SQL:
- Use proper JOIN syntax when relating orders to products
- Handle NULL values gracefully
- Use appropriate aggregate functions (COUNT, SUM, AVG)
- Order results meaningfully when appropriate

After executing a query, format the results in a natural, readable way.
"""

    def query(self, user_message: str) -> str:
        """
        Process natural language query and return answer.

        Args:
            user_message: User's natural language question

        Returns:
            Natural language answer based on query results
        """
        try:
            # Step 1: Generate SQL from natural language
            sql_query = self._generate_sql(user_message)

            if not sql_query:
                return "I couldn't generate a SQL query for that question. Could you rephrase it?"

            # Step 2: Execute SQL
            results = self._execute_sql(sql_query)

            if results is None:
                return "There was an error executing the query."

            # Step 3: Format results as natural language
            answer = self._format_results(user_message, sql_query, results)

            return answer

        except Exception as e:
            return f"Error processing query: {str(e)}"

    def _generate_sql(self, question: str) -> Optional[str]:
        """
        Use LLM to convert natural language to SQL.

        Args:
            question: Natural language question

        Returns:
            SQL query string or None
        """
        prompt = f"""Convert this question to a SQL query:

Question: {question}

Return ONLY the SQL query, nothing else. No explanations, no markdown, just the SQL."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            sql = response.content[0].text.strip()

            # Clean up common formatting issues
            sql = sql.replace("```sql", "").replace("```", "").strip()

            # Basic safety check - only allow SELECT
            sql_upper = sql.upper().strip()
            if not sql_upper.startswith("SELECT"):
                return None

            # Block dangerous keywords
            dangerous = ["DELETE", "DROP", "INSERT", "UPDATE", "ALTER", "CREATE"]
            for keyword in dangerous:
                if keyword in sql_upper:
                    return None

            return sql

        except Exception as e:
            print(f"Error generating SQL: {e}")
            return None

    def _execute_sql(self, sql: str) -> Optional[list]:
        """
        Execute SQL query safely.

        Args:
            sql: SQL query to execute

        Returns:
            List of result tuples or empty list, None on error
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()

            cursor.execute(sql)
            results = cursor.fetchall()

            # Convert to list of dicts for easier processing
            results_list = []
            for row in results:
                results_list.append(dict(row))

            conn.close()

            return results_list

        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            return None
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return None

    def _format_results(
        self,
        question: str,
        sql: str,
        results: list
    ) -> str:
        """
        Format SQL results as natural language.

        Args:
            question: Original question
            sql: SQL query that was executed
            results: Query results

        Returns:
            Natural language formatted answer
        """
        if not results:
            return "No results found for that query."

        # If single value (like COUNT), return it directly
        if len(results) == 1 and len(results[0]) == 1:
            value = list(results[0].values())[0]
            return f"Result: {value}"

        # For multiple results, format as a readable list
        result_count = len(results)

        if result_count <= 5:
            # Show all results
            formatted = f"Found {result_count} result(s):\n\n"
            for i, row in enumerate(results, 1):
                formatted += f"{i}. "
                formatted += ", ".join(f"{k}: {v}" for k, v in row.items())
                formatted += "\n"
        else:
            # Show first 5 and indicate there are more
            formatted = f"Found {result_count} result(s). Showing first 5:\n\n"
            for i, row in enumerate(results[:5], 1):
                formatted += f"{i}. "
                formatted += ", ".join(f"{k}: {v}" for k, v in row.items())
                formatted += "\n"
            formatted += f"\n... and {result_count - 5} more results."

        return formatted.strip()

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with database stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            # Product stats
            cursor.execute("SELECT COUNT(*) FROM products")
            stats["total_products"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
            stats["categories"] = cursor.fetchone()[0]

            # Order stats
            cursor.execute("SELECT COUNT(*) FROM orders")
            stats["total_orders"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
            stats["completed_orders"] = cursor.fetchone()[0]

            conn.close()

            return stats

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Quick test
    print("Initializing SQL Agent...")
    agent = SQLAgent()

    print("\nDatabase stats:")
    print(agent.get_stats())

    print("\n" + "="*60)
    print("Testing SQL Agent")
    print("="*60)

    test_questions = [
        "How many products are there?",
        "Show all electronics",
        "What are the top 3 most expensive products?",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        answer = agent.query(question)
        print(f"A: {answer}")
        print("-" * 60)
