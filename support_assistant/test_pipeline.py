"""
Test Pipeline Module

Executes test queries against the compiled LangGraph StateGraph,
validates the outputs using the Pydantic AnswerResponse schema,
and outputs formatted JSON.
"""

import json
from graph import graph
from schema import AnswerResponse


def run_test_cases() -> None:
    """
    Invokes the support assistant graph on both policy-related and general queries,
    validates the results against AnswerResponse, and prints JSON outputs.
    """
    print("=" * 70)
    # Test Case 1: Policy Query (Should route to retrieve_and_answer)
    policy_query = "What is the standard delivery fee for orders?"
    print(f"Test Case 1: Policy Query -> '{policy_query}'")
    print("=" * 70)

    # Invoke graph
    state_policy = graph.invoke({"query": policy_query})

    # Validate against AnswerResponse schema
    validated_policy = AnswerResponse(
        answer=state_policy["answer"],
        sources=state_policy["sources"],
        confidence=state_policy["confidence"]
    )

    print("\nState Output keys:", list(state_policy.keys()))
    print("Validated JSON Output:")
    print(validated_policy.model_dump_json(indent=2))
    print("=" * 70 + "\n")

    print("=" * 70)
    # Test Case 2: General Query (Should route to direct_answer)
    general_query = "What is the capital of France?"
    print(f"Test Case 2: General Query -> '{general_query}'")
    print("=" * 70)

    # Invoke graph
    state_general = graph.invoke({"query": general_query})

    # Validate against AnswerResponse schema
    validated_general = AnswerResponse(
        answer=state_general["answer"],
        sources=state_general["sources"],
        confidence=state_general["confidence"]
    )

    print("\nState Output keys:", list(state_general.keys()))
    print("Validated JSON Output:")
    print(validated_general.model_dump_json(indent=2))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_test_cases()
