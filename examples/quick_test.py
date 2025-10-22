"""Quick test with one test case."""

from sae import AUTWrapper, run_evaluation


class DummyAgent(AUTWrapper):
    """Mock agent for testing SAE pipeline."""

    def __init__(self):
        self.counter = 0

    def invoke(self, message: str) -> str:
        """Process message and return response."""
        self.counter += 1

        if "error" in message.lower():
            return "ERROR: Something went wrong!"
        elif "count" in message.lower():
            return f"Current count: {self.counter}"
        elif "hello" in message.lower():
            return "Hello! I'm DummyAgent. How can I help you?"
        else:
            return f"Received: {message} (processed)"

    def reset(self):
        """Reset agent state for new test."""
        self.counter = 0


if __name__ == "__main__":
    print("Running quick test with 1 test case...")
    run_evaluation(
        aut_class=DummyAgent,
        test_cases_xlsx="./dummy_tests_quick.xlsx",
        output_dir="./quick_test_results",
        timeout_seconds=60
    )
