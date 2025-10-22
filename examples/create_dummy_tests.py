"""Script to create dummy test cases Excel file."""

import pandas as pd

# Define test cases
test_cases = [
    {
        "test_name": "basic_response",
        "what_to_test": "Send a simple 'hello' message",
        "expected_behavior": "Agent responds with a greeting",
        "notes": "Basic sanity check"
    },
    {
        "test_name": "state_tracking",
        "what_to_test": "Send multiple messages and check counter",
        "expected_behavior": "Counter should increment with each call",
        "notes": "Verify state persistence across turns"
    },
    {
        "test_name": "error_handling",
        "what_to_test": "Send message containing 'error'",
        "expected_behavior": "Agent returns error message gracefully",
        "notes": "Test error handling behavior"
    },
    {
        "test_name": "echo_behavior",
        "what_to_test": "Send an arbitrary message like 'testing 123'",
        "expected_behavior": "Agent echoes back the message",
        "notes": "Test default processing behavior"
    },
    {
        "test_name": "count_query",
        "what_to_test": "Ask 'what is the count?'",
        "expected_behavior": "Agent returns current counter value",
        "notes": "Test ability to query internal state"
    }
]

# Create DataFrame and save to Excel
df = pd.DataFrame(test_cases)
df.to_excel("dummy_tests.xlsx", index=False)

print("Created dummy_tests.xlsx with 5 test cases")
print("\nTest cases:")
for i, tc in enumerate(test_cases, 1):
    print(f"{i}. {tc['test_name']}: {tc['what_to_test']}")
