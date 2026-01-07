# tools/policy_lookup.py
"""
Fetch policy information for the tri-agent e-commerce system.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger

# Example policy database (can be replaced with real DB or vector search)
POLICY_DB = {
    "refund": "Refunds are eligible within 14 days of delivery. Items must be in original condition.",
    "return": "Customers can return items within 14 days of receiving them. Return shipping is free for orders over $50.",
    "damaged": "If an item arrives damaged, customers should report within 48 hours to receive replacement or refund.",
    "late delivery": "Delivery delays due to weather or logistics are notified via email. No compensation is guaranteed.",
    "wrong item": "If the wrong item is delivered, please contact support for replacement within 7 days."
}

def fetch_policy(user_input: str) -> str:
    """
    Fetch relevant policy text based on keywords in the user input.

    Args:
        user_input (str): The complaint or query text.

    Returns:
        str: Relevant policy text or a fallback message.
    """
    input_lower = user_input.lower()
    matched_policies = []

    # Look for keywords in the input
    for keyword, policy_text in POLICY_DB.items():
        if keyword in input_lower:
            matched_policies.append(policy_text)

    if matched_policies:
        response = " | ".join(matched_policies)
    else:
        response = "No specific policy found. Please refer to our standard support guidelines."

    logger.info(f"Policy lookup for input '{user_input}': {response}")
    return response


# Optional self-test
if __name__ == "__main__":
    sample_inputs = [
        "I want a refund for my damaged package",
        "My delivery is late",
        "I received the wrong item"
    ]
    for query in sample_inputs:
        print(fetch_policy(query))
