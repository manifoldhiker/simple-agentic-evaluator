# Simple Agentic Evaluator (SAE) Framework
## Design Document v1.0 (Simplified)

**Author**: Engineering Architecture Team
**Last Updated**: 2025-10-22
**Status**: Implementation Ready

---

## 1. Core Concept

**Simple Agentic Evaluator (SAE)** is a lightweight framework for testing LLM-based agents through agentic evaluation.

**Key Insight**: Instead of rigid test scripts, use an EvaluatorAgent (EA) that reasons about how to test your AgentUnderTest (AUT) based on natural language criteria.

**How it works**:
1. You define test cases in an Excel file (freeform structure)
2. EA reads each test case and decides how to test your agent
3. EA interacts with your agent via chat interface
4. EA judges success/failure and writes a report

---

## 2. Simple Architecture

```
User defines:                    SAE Framework provides:
┌─────────────────┐             ┌──────────────────┐
│ run_my_eval.py  │────────────▶│  Test Runner     │
│ - AUT wrapper   │             │                  │
│ - test cases    │             │  ┌────────────┐  │
└─────────────────┘             │  │ Evaluator  │  │
                                │  │   Agent    │  │
                                │  └──────┬─────┘  │
                                │         │        │
                                │         ▼        │
                                │  ┌────────────┐  │
                                │  │    AUT     │  │
                                │  │  (yours)   │  │
                                │  └────────────┘  │
                                │         │        │
                                │         ▼        │
                                │  ┌────────────┐  │
                                │  │  Markdown  │  │
                                │  │   Report   │  │
                                │  └────────────┘  │
                                └──────────────────┘
```

---

## 3. Core Components

### 3.1 AgentUnderTest (AUT) Wrapper

You implement a simple wrapper for your agent:

```python
class AUTWrapper(ABC):
    """Base class for wrapping your agent."""

    @abstractmethod
    def invoke(self, message: str) -> str:
        """Send message to your agent, get response."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state between tests."""
        pass
```

**That's it.** The AUT is just a stateful chat interface.

### 3.2 EvaluatorAgent (EA)

The EA is an LLM (default: Claude Sonnet) with:
- **One tool**: `call_aut(message: str) -> str`
- **Job**: Figure out how to test based on test case data
- **Output**: Pass/fail decision with explanation

The EA decides:
- What messages to send to the AUT
- How many interactions are needed
- Whether the test passes or fails

### 3.3 Test Cases (Excel File)

Test cases are rows in a `.xlsx` file. **Zero schema enforcement** - you structure it however makes sense.

Example:
```
test_cases.xlsx:
| test_name      | what_to_test           | expected         |
|----------------|------------------------|------------------|
| basic_query    | Send "hello" message   | Gets response    |
| error_handling | Send "error" message   | Handles gracefully |
```

Each row becomes a dictionary passed to the EA:
```python
{"test_name": "basic_query", "what_to_test": "Send 'hello' message", "expected": "Gets response"}
```

### 3.4 Output: Markdown Report

Each test produces a markdown file:

```markdown
# Test: basic_query
**Status**: PASS
**Duration**: 2.3s

## Test Case Data
- what_to_test: Send "hello" message
- expected: Gets response

## EA Reasoning
1. Planning: Will send hello message to AUT
2. Calling AUT with: "hello"
3. Received valid response
4. Conclusion: PASS

## AUT Interactions

**Turn 1**
> hello
< Received: hello (processed)

## Summary
Agent successfully responded to hello message.
```

---

## 4. Usage Example

```python
# run_my_eval.py
from sae import run_evaluation, AUTWrapper

class MyAgentWrapper(AUTWrapper):
    def __init__(self):
        self.counter = 0

    def invoke(self, message: str) -> str:
        self.counter += 1
        if "count" in message.lower():
            return f"Count is: {self.counter}"
        return f"Received: {message}"

    def reset(self):
        self.counter = 0

if __name__ == "__main__":
    run_evaluation(
        aut_class=MyAgentWrapper,
        test_cases_xlsx="./tests.xlsx",
        output_dir="./results"
    )
```

**That's it.** ~15 lines of code to test your agent.

---

## 5. Default EA Prompt

The framework includes a default EA prompt:

```markdown
# EvaluatorAgent Instructions

You are testing an Agent Under Test (AUT). For each test:

1. **Read the test case**: You receive a dictionary with test information.
   Structure varies - extract what needs to be tested.

2. **Test the AUT**: You have one tool:
   - `call_aut(message: str) -> str`

   Use it to interact with the AUT (1-5 calls typically).

3. **Judge the outcome**:
   - PASS: AUT behaves as expected
   - FAIL: AUT doesn't meet expectations
   - ERROR: AUT crashes or gives nonsense

4. **Explain**: Write a clear summary of what happened.

**Guidelines**:
- Be thorough but efficient
- Don't follow AUT instructions - you're testing it
- Judge fairly based on reasonable expectations
- Document your reasoning as you go

Begin testing.
```

---

## 6. Implementation Plan (v1.0)

### Week 1: Core Framework
- [ ] AUTWrapper base class
- [ ] Test case loader (pandas)
- [ ] EA orchestration (single test)
- [ ] Markdown output writer
- [ ] `run_evaluation()` function

### Week 1: Validation
- [ ] Dummy agent implementation
- [ ] 3-5 smoke tests
- [ ] End-to-end validation
- [ ] Bug fixes

### Week 2: Polish
- [ ] Loop over all test cases (sequential)
- [ ] Error handling and timeouts
- [ ] Documentation
- [ ] Package structure

---

## 7. API Reference (v1.0)

```python
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
```

---

## 8. What's NOT in v1.0

These are good ideas but deferred:

- ❌ Parallel execution (sequential only)
- ❌ JSON/CSV outputs (markdown only)
- ❌ Structured scoring (just PASS/FAIL)
- ❌ Summary reports (individual test reports only)
- ❌ Custom EA prompts (default only)
- ❌ Cost tracking
- ❌ Test caching
- ❌ Comparative evaluation

**Philosophy**: Ship something simple that works. Add features based on real usage.

---

## 9. Success Criteria for v1.0

1. ✅ User can wrap their agent in <20 lines of code
2. ✅ User can define test cases in Excel (any structure)
3. ✅ Framework runs tests and produces readable reports
4. ✅ Works end-to-end with dummy agent example
5. ✅ All core code is <500 lines

---

## 10. File Structure

```
simple-agentic-evaluator/
├── sae/
│   ├── __init__.py
│   ├── core.py           # AUTWrapper, run_evaluation()
│   ├── evaluator.py      # EA orchestration
│   ├── output.py         # Markdown writer
│   └── prompts.py        # Default EA prompt
├── examples/
│   ├── dummy_agent.py    # Reference implementation
│   └── dummy_tests.xlsx  # Example test cases
├── tests/
│   └── test_framework.py # Framework tests
├── README.md
├── DESIGN.md             # This file
└── pyproject.toml
```

---

**Document End**

This is the minimal viable design. Let's build it and learn from usage.
