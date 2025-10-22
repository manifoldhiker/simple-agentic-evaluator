"""EvaluatorAgent orchestration."""

import json
import time
from datetime import datetime
from typing import Any
import anthropic
from .core import AUTWrapper
from .prompts import DEFAULT_EVALUATOR_PROMPT


def run_single_test(
    aut: AUTWrapper,
    test_case: dict,
    test_id: str,
    timeout_seconds: int = 300,
    evaluator_model: str = "claude-sonnet-4-5-20250929"
) -> dict:
    """
    Run a single test case with the EvaluatorAgent.

    Args:
        aut: Agent under test instance
        test_case: Test case data (dict from Excel row)
        test_id: Unique test identifier
        timeout_seconds: Timeout for this test
        evaluator_model: Model to use for EA

    Returns:
        Test result dictionary
    """
    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Reset AUT state
    aut.reset()

    # Initialize tracking
    ea_reasoning_log = []
    aut_interactions = []

    # Define the call_aut tool
    call_aut_tool = {
        "name": "call_aut",
        "description": "Send a message to the Agent Under Test and receive response.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Natural language instruction or query to send to the AUT"
                }
            },
            "required": ["message"]
        }
    }

    # Build initial message for EA
    test_case_json = json.dumps(test_case, indent=2)
    initial_message = f"""You are testing an agent. Here is the test case:

{test_case_json}

Use the call_aut tool to interact with the agent and determine if it passes or fails this test.
When you're done, provide your final judgment."""

    # Initialize Anthropic client
    client = anthropic.Anthropic()

    # Agentic loop
    messages = [{"role": "user", "content": initial_message}]
    turn = 0
    max_turns = 20  # Safety limit

    try:
        while turn < max_turns:
            turn += 1

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                return {
                    "test_id": test_id,
                    "status": "TIMEOUT",
                    "summary": f"Test exceeded {timeout_seconds}s timeout",
                    "test_case": test_case,
                    "ea_reasoning_log": ea_reasoning_log,
                    "aut_interactions": aut_interactions,
                    "duration_seconds": time.time() - start_time,
                    "timestamp": timestamp
                }

            # Call EA
            response = client.messages.create(
                model=evaluator_model,
                max_tokens=4096,
                system=DEFAULT_EVALUATOR_PROMPT,
                messages=messages,
                tools=[call_aut_tool]
            )

            # Log EA's thinking
            for content in response.content:
                if content.type == "text":
                    ea_reasoning_log.append(f"[Turn {turn}] {content.text}")

            # Check stop reason
            if response.stop_reason == "end_turn":
                # EA is done, extract final judgment
                final_text = ""
                for content in response.content:
                    if content.type == "text":
                        final_text += content.text

                status, summary = parse_final_judgment(final_text)

                duration = time.time() - start_time
                return {
                    "test_id": test_id,
                    "status": status,
                    "summary": summary,
                    "test_case": test_case,
                    "ea_reasoning_log": ea_reasoning_log,
                    "aut_interactions": aut_interactions,
                    "duration_seconds": duration,
                    "timestamp": timestamp
                }

            elif response.stop_reason == "tool_use":
                # EA wants to call AUT
                # Add assistant message to history
                messages.append({"role": "assistant", "content": response.content})

                # Process tool calls
                tool_results = []
                for content in response.content:
                    if content.type == "tool_use":
                        tool_name = content.name
                        tool_input = content.input

                        if tool_name == "call_aut":
                            # Call the AUT
                            aut_message = tool_input["message"]
                            try:
                                aut_response = aut.invoke(aut_message)
                            except Exception as e:
                                aut_response = f"ERROR: {str(e)}"

                            # Record interaction
                            aut_interactions.append({
                                "turn": turn,
                                "message": aut_message,
                                "response": aut_response,
                                "timestamp": datetime.utcnow().isoformat() + "Z"
                            })

                            # Return tool result
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": aut_response
                            })

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})

            else:
                # Unexpected stop reason
                return {
                    "test_id": test_id,
                    "status": "ERROR",
                    "summary": f"Unexpected stop reason: {response.stop_reason}",
                    "test_case": test_case,
                    "ea_reasoning_log": ea_reasoning_log,
                    "aut_interactions": aut_interactions,
                    "duration_seconds": time.time() - start_time,
                    "timestamp": timestamp
                }

        # Hit max turns
        return {
            "test_id": test_id,
            "status": "ERROR",
            "summary": f"EA exceeded max turns ({max_turns})",
            "test_case": test_case,
            "ea_reasoning_log": ea_reasoning_log,
            "aut_interactions": aut_interactions,
            "duration_seconds": time.time() - start_time,
            "timestamp": timestamp
        }

    except Exception as e:
        # Catch any errors
        return {
            "test_id": test_id,
            "status": "ERROR",
            "summary": f"Exception during test: {str(e)}",
            "test_case": test_case,
            "ea_reasoning_log": ea_reasoning_log,
            "aut_interactions": aut_interactions,
            "duration_seconds": time.time() - start_time,
            "timestamp": timestamp,
            "error_details": str(e)
        }


def parse_final_judgment(text: str) -> tuple[str, str]:
    """
    Parse final judgment from EA's text output.

    Args:
        text: EA's final text output

    Returns:
        (status, summary) tuple
    """
    # Look for FINAL_JUDGMENT format
    if "FINAL_JUDGMENT:" in text:
        lines = text.split("\n")
        status = "FAIL"
        summary = ""

        for line in lines:
            if line.startswith("STATUS:"):
                status = line.replace("STATUS:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()

        # Validate status
        valid_statuses = ["PASS", "FAIL", "ERROR"]
        if status not in valid_statuses:
            status = "FAIL"

        if not summary:
            summary = "EA completed test but provided no summary"

        return status, summary

    # Fallback: look for status keywords in text
    text_upper = text.upper()
    if "PASS" in text_upper and "FAIL" not in text_upper:
        return "PASS", text.strip()
    elif "ERROR" in text_upper:
        return "ERROR", text.strip()
    else:
        return "FAIL", text.strip()
