"""
API Client Test Module

Sends query payloads to the FastAPI endpoint at http://127.0.0.1:7860/ask
and prints response payloads for documentation.
"""

import json
import urllib.request


def run_api_tests() -> None:
    """
    Sends a policy query and a general query to the local server,
    retrieves response payloads, and formats them in JSON.
    """
    url = "http://127.0.0.1:7860/ask"

    # Test Case 1: Policy query
    policy_payload = {"query": "How can I return damaged groceries?"}
    print(f"Executing POST Request with payload: {policy_payload}")

    req_policy = urllib.request.Request(
        url,
        data=json.dumps(policy_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req_policy) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("Response raw JSON:")
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error executing policy request: {e}")

    print("-" * 75)

    # Test Case 2: General query
    general_payload = {"query": "What is the capital of Japan?"}
    print(f"Executing POST Request with payload: {general_payload}")

    req_general = urllib.request.Request(
        url,
        data=json.dumps(general_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req_general) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("Response raw JSON:")
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error executing general request: {e}")


if __name__ == "__main__":
    run_api_tests()
