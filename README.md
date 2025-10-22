# Simple Agentic Evaluator (SAE)

A lightweight framework for testing LLM-based agents through agentic evaluation.

## Core Concept

Instead of rigid test scripts, SAE uses an **EvaluatorAgent (EA)** that reasons about how to test your **AgentUnderTest (AUT)** based on natural language criteria.

**How it works:**
1. Define test cases in an Excel file (freeform structure)
2. EA reads each test case and decides how to test your agent
3. EA interacts with your agent via chat interface
4. EA judges success/failure and writes a report

## Installation

```bash
pip install -e .
```

## Requirements

- Python 3.9+
- Anthropic API key (set `ANTHROPIC_API_KEY` environment variable)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### 1. Wrap Your Agent

Create a wrapper for your agent that implements the `AUTWrapper` interface:

```python
from sae import AUTWrapper

class MyAgentWrapper(AUTWrapper):
    def __init__(self):
        # Initialize your agent
        self.agent = YourAgent()

    def invoke(self, message: str) -> str:
        # Send message to agent, return response
        return self.agent.chat(message)

    def reset(self):
        # Reset agent state between tests
        self.agent.clear_history()
```

### 2. Create Test Cases (Excel)

Create an `.xlsx` file with your test cases. **No schema enforced** - structure it however makes sense:

| test_name | what_to_test | expected_behavior |
|-----------|--------------|-------------------|
| basic_query | Send "hello" message | Gets response |
| error_handling | Send invalid input | Handles gracefully |

### 3. Run Evaluation

```python
from sae import run_evaluation
from my_agent import MyAgentWrapper

run_evaluation(
    aut_class=MyAgentWrapper,
    test_cases_xlsx="./test_cases.xlsx",
    output_dir="./results"
)
```

That's it! SAE will:
- Load test cases from Excel
- Run each test with the EvaluatorAgent
- Generate markdown reports in the output directory

## Examples

### Example 1: Dummy Agent

See `examples/dummy_agent.py` for a basic working example:

```bash
cd examples
python create_dummy_tests.py  # Generate test cases
python dummy_agent.py          # Run evaluation
```

This will:
1. Create `dummy_tests.xlsx` with 5 test cases
2. Run evaluation with DummyAgent
3. Generate reports in `dummy_eval_results/`

### Example 2: SQL Agent

See `examples/sql_agent/` for a real-world SQL agent that converts natural language to SQL:

```bash
cd examples/sql_agent
python db_setup.py             # Create database
python create_test_cases.py    # Generate test cases
python run_sql_eval.py         # Run evaluation
```

This demonstrates:
- Text-to-SQL conversion with Claude
- Safe SQL execution on SQLite database
- 10 test cases covering queries, joins, aggregations
- E-commerce database with products and orders

See `examples/sql_agent/README.md` for details.

## Test Case Format

SAE uses a **zero-schema** approach. Your Excel file can have any columns you want. Common patterns:

**Option 1: Question-based**
```
| question | expected_result | notes |
```

**Option 2: Scenario-based**
```
| scenario | agent_should | verification |
```

**Option 3: Instruction-based**
```
| test_instruction | pass_criteria | context |
```

The EA receives the entire row as a dictionary and figures out what to test.

## Output Format

Each test produces a markdown report:

```markdown
# Test: TC001
**Status**: ✓ PASS
**Duration**: 2.3s

## Test Case Data
{your test case data}

## Summary
{EA's explanation of what happened}

## EvaluatorAgent Reasoning Log
- Planning: Will send hello message
- Calling AUT with: "hello"
- Received valid response
- Conclusion: PASS

## AUT Interaction Trace
**Turn 1**
> hello
< Hello! How can I help?
```

## API Reference

### `run_evaluation()`

```python
run_evaluation(
    aut_class: Type[AUTWrapper],
    test_cases_xlsx: str,
    output_dir: str = "./eval_results",
    timeout_seconds: int = 300,
    evaluator_model: str = "claude-sonnet-4-5-20250929"
)
```

**Parameters:**
- `aut_class`: Your AUT wrapper class
- `test_cases_xlsx`: Path to Excel file with test cases
- `output_dir`: Where to write markdown reports (default: `./eval_results`)
- `timeout_seconds`: Per-test timeout (default: 300)
- `evaluator_model`: LLM model for EvaluatorAgent

### `AUTWrapper` Interface

```python
class AUTWrapper(ABC):
    @abstractmethod
    def invoke(self, message: str) -> str:
        """Send message to agent, get response."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state between tests."""
        pass
```

## Design Philosophy

**v1.0 is intentionally minimal:**
- ✅ Sequential execution (no parallel)
- ✅ Markdown output only
- ✅ Simple PASS/FAIL status
- ✅ Default EA prompt only
- ✅ <500 lines of core code

**What's NOT in v1.0:**
- ❌ Parallel execution
- ❌ JSON/CSV outputs
- ❌ Structured scoring
- ❌ Custom EA prompts
- ❌ Cost tracking
- ❌ Test caching

We'll add features based on real usage patterns.

## Project Structure

```
simple-agentic-evaluator/
├── sae/
│   ├── __init__.py       # Public API
│   ├── core.py           # AUTWrapper, run_evaluation()
│   ├── evaluator.py      # EA orchestration
│   ├── output.py         # Markdown writer
│   └── prompts.py        # Default EA prompt
├── examples/
│   ├── dummy_agent.py    # Reference implementation
│   └── dummy_tests.xlsx  # Example test cases
├── README.md
├── DESIGN.md             # Design document
└── pyproject.toml
```

## Contributing

See `DESIGN.md` for architecture details and implementation roadmap.

## License

MIT

## Credits

Built with Claude Code by Anthropic.
