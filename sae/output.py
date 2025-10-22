"""Output formatting for test results."""

import json
from pathlib import Path


def write_markdown_report(test_result: dict, output_path: Path) -> None:
    """
    Write test result as markdown report.

    Args:
        test_result: Test result dictionary
        output_path: Path to write markdown file
    """
    # Status emoji
    status_emoji = {
        "PASS": "✓",
        "FAIL": "✗",
        "ERROR": "⚠",
        "TIMEOUT": "⏱"
    }

    status = test_result["status"]
    emoji = status_emoji.get(status, "?")

    # Build markdown content
    lines = []

    # Header
    lines.append(f"# Test: {test_result['test_id']}")
    lines.append(f"**Status**: {emoji} {status}")
    lines.append(f"**Duration**: {test_result['duration_seconds']:.1f}s")
    lines.append(f"**Timestamp**: {test_result['timestamp']}")
    lines.append("")

    # Test Case Data
    lines.append("## Test Case Data")
    lines.append("")
    test_case = test_result.get("test_case", {})
    if test_case:
        lines.append("```json")
        lines.append(json.dumps(test_case, indent=2))
        lines.append("```")
    else:
        lines.append("No test case data")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(test_result.get("summary", "No summary provided"))
    lines.append("")

    # EA Reasoning Log
    lines.append("## EvaluatorAgent Reasoning Log")
    lines.append("")
    ea_log = test_result.get("ea_reasoning_log", [])
    if ea_log:
        for entry in ea_log:
            lines.append(f"- {entry}")
    else:
        lines.append("No reasoning log recorded")
    lines.append("")

    # AUT Interactions
    lines.append("## AUT Interaction Trace")
    lines.append("")
    interactions = test_result.get("aut_interactions", [])
    if interactions:
        for interaction in interactions:
            lines.append(f"**Turn {interaction['turn']}**")
            lines.append("```")
            lines.append(f"> {interaction['message']}")
            lines.append(f"< {interaction['response']}")
            lines.append("```")
            lines.append("")
    else:
        lines.append("No AUT interactions recorded")
    lines.append("")

    # Error details if present
    if "error_details" in test_result and test_result["error_details"]:
        lines.append("## Error Details")
        lines.append("")
        lines.append("```")
        lines.append(test_result["error_details"])
        lines.append("```")
        lines.append("")

    # Write to file
    content = "\n".join(lines)
    output_path.write_text(content)
