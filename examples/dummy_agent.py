"""Example: Dummy agent for testing SAE framework."""

from sae import AUTWrapper, run_evaluation


class DummyAgent(AUTWrapper):
    """
    Mock agent for testing SAE pipeline.

    This agent simulates different behaviors:
    - Normal responses: echoes back the message
    - Error handling: returns error for messages containing "error"
    - State tracking: maintains a counter
    """

    def __init__(self):
        self.counter = 0
        self.name = "DummyAgent"

    def invoke(self, message: str) -> str:
        """Process message and return response."""
        self.counter += 1

        # Simulate different behaviors
        if "error" in message.lower():
            return "ERROR: Something went wrong!"
        elif "count" in message.lower():
            return f"Current count: {self.counter}"
        elif "hello" in message.lower():
            return "Hello! I'm DummyAgent. How can I help you?"
        elif "reset" in message.lower():
            return "I cannot reset myself from a message, but my state persists across calls."
        else:
            return f"Received: {message} (processed)"

    def reset(self):
        """Reset agent state for new test."""
        self.counter = 0


if __name__ == "__main__":
    # Run evaluation with dummy agent
    run_evaluation(
        aut_class=DummyAgent,
        test_cases_xlsx="./dummy_tests.xlsx",
        output_dir="./dummy_eval_results",
        timeout_seconds=60
    )
