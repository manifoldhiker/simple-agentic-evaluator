"""Core classes and functions for Simple Agentic Evaluator."""

from abc import ABC, abstractmethod
from typing import Type
import pandas as pd
from pathlib import Path


class AUTWrapper(ABC):
    """Base class for wrapping your agent under test."""

    @abstractmethod
    def invoke(self, message: str) -> str:
        """
        Send message to your agent, get response.

        Args:
            message: User message to send to agent

        Returns:
            Agent's text response
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state between tests."""
        pass


def load_test_cases(xlsx_path: str) -> list[dict]:
    """
    Load test cases from Excel file.

    Args:
        xlsx_path: Path to Excel file with test cases

    Returns:
        List of test case dictionaries (one per row)
    """
    df = pd.read_excel(xlsx_path)
    # Convert each row to a dictionary
    test_cases = df.to_dict('records')
    return test_cases


def run_evaluation(
    aut_class: Type[AUTWrapper],
    test_cases_xlsx: str,
    output_dir: str = "./eval_results",
    timeout_seconds: int = 300,
    evaluator_model: str = "claude-sonnet-4-5-20250929"
) -> None:
    """
    Run evaluation suite against AUT.

    Args:
        aut_class: Your AUT wrapper class
        test_cases_xlsx: Path to Excel file with test cases
        output_dir: Where to write markdown reports
        timeout_seconds: Per-test timeout
        evaluator_model: LLM for EvaluatorAgent
    """
    from .evaluator import run_single_test

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load test cases
    print(f"Loading test cases from {test_cases_xlsx}...")
    test_cases = load_test_cases(test_cases_xlsx)
    print(f"Found {len(test_cases)} test cases")

    # Run each test sequentially
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Running test {i}/{len(test_cases)}")
        print(f"{'='*60}")

        # Create AUT instance for this test
        aut = aut_class()

        # Run the test
        test_result = run_single_test(
            aut=aut,
            test_case=test_case,
            test_id=f"TC{i:03d}",
            timeout_seconds=timeout_seconds,
            evaluator_model=evaluator_model
        )

        # Write result
        from .output import write_markdown_report
        report_path = output_path / f"{test_result['test_id']}.md"
        write_markdown_report(test_result, report_path)

        print(f"✓ Test {test_result['test_id']}: {test_result['status']}")
        print(f"  Report: {report_path}")

    print(f"\n{'='*60}")
    print(f"Evaluation complete! Results in: {output_dir}")
    print(f"{'='*60}")
