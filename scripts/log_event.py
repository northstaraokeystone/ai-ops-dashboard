import argparse
import json
import uuid
import requests


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the log_event script.

    Why: Centralizes arg handling for maintainability (SRP: one function for parsing),
    using argparse for stdlib CLI with defaults/reqs, aligning with Pragmatic Programmer
    for configurable scripts and Beck XP for testable inputs in CI workflows.
    """
    parser = argparse.ArgumentParser(
        description="Log CI/CD events to Fulcrum API interaction endpoint."
    )
    parser.add_argument(
        "--status",
        required=True,
        type=str,
        help="Event status (e.g., 'success', 'failure').",
    )
    parser.add_argument(
        "--error-log", default=None, type=str, help="Optional error message log."
    )
    parser.add_argument(
        "--commit-hash", default=None, type=str, help="Optional Git commit hash."
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/interaction/",
        type=str,
        help="API endpoint URL.",
    )
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> dict:
    """Construct JSON payload matching InteractionCreate schema from args.

    Why: Acts as anti-corruption layer between CLI args and API schema, ensuring
    data integrity with explicit mapping/defaults to prevent TypeErrors/mismatches,
    supporting AI trust fabric by logging complete, traceable events for ML audits
    (e.g., details dict for interpretable failure analysis, avoiding bias from incomplete data).
    """
    details = {
        "status": args.status,
        "error_log": args.error_log,
        "commit_hash": args.commit_hash,
    }
    payload = {
        "agent_id": str(
            uuid.UUID("00000000-0000-0000-0000-000000000001")
        ),  # Fixed "CI Agent" UUID
        "action_type": 100,  # Fixed for CI events
        "payload": "ci_event",  # Minimal placeholder; could encode details if needed
        "environment_hash": "ci_env",  # Fixed placeholder
        "session_id": "ci_session",  # Fixed for schema
        "details": details,
        "causality_id": None,  # Optional, default None
    }
    return payload


if __name__ == "__main__":
    args = parse_arguments()
    payload = build_payload(args)

    try:
        response = requests.post(args.api_url, json=payload, timeout=10)
        response.raise_for_status()  # Raise on HTTP errors (4xx/5xx)

        # Parse response for ID (assume JSON with 'id' key; adjust if schema differs)
        data = response.json()
        interaction_id = data.get("id", "unknown")
        print(f"Event logged successfully. Interaction ID: {interaction_id}")

    except requests.exceptions.HTTPError as http_err:
        print(
            f"HTTP error occurred: {http_err} - Status: {response.status_code} - Response: {response.text}"
        )
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to parse response JSON.")
    except TypeError as type_err:
        print(f"Type error occurred: {type_err} - Check payload/schema alignment.")
    except Exception as err:
        print(f"Unexpected error: {err}")
