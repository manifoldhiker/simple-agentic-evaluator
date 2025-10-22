"""Run SQL Agent evaluation with SAE framework."""

import sys
from pathlib import Path

# Add parent directory to path to import sae
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sae import AUTWrapper, run_evaluation
from sql_agent import SQLAgent, create_database


class SQLAgentWrapper(AUTWrapper):
    """
    Wrapper for SQL Agent to use with SAE framework.

    Creates a fresh database for each evaluation run and
    wraps the SQL Agent's query interface.
    """

    def __init__(self):
        """Initialize SQL Agent with fresh database."""
        # Create database in the sql_agent directory
        self.db_path = Path(__file__).parent / "test_ecommerce.db"

        # Create and populate database
        print(f"Setting up test database: {self.db_path}")
        create_database(str(self.db_path))

        # Initialize SQL Agent
        self.agent = SQLAgent(db_path=str(self.db_path))

        print("SQL Agent initialized and ready for testing")

    def invoke(self, message: str) -> str:
        """
        Send query to SQL Agent.

        Args:
            message: Natural language query

        Returns:
            SQL Agent's response
        """
        return self.agent.query(message)

    def reset(self) -> None:
        """Reset conversation history (database stays the same)."""
        self.agent.reset_conversation()

    def get_stats(self) -> dict:
        """Get database statistics for debugging."""
        return self.agent.get_stats()


if __name__ == "__main__":
    print("="*60)
    print("SQL Agent Evaluation with SAE Framework")
    print("="*60)
    print()

    # Check if test cases file exists
    test_cases_file = Path(__file__).parent / "sql_agent_tests.xlsx"

    if not test_cases_file.exists():
        print(f"ERROR: Test cases file not found: {test_cases_file}")
        print("Please create sql_agent_tests.xlsx first")
        sys.exit(1)

    # Run evaluation
    run_evaluation(
        aut_class=SQLAgentWrapper,
        test_cases_xlsx=str(test_cases_file),
        output_dir=str(Path(__file__).parent / "sql_eval_results"),
        timeout_seconds=120  # 2 minutes per test
    )

    print()
    print("="*60)
    print("Evaluation complete!")
    print("="*60)
