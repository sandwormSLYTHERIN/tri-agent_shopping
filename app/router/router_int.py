import re
from typing import Literal, Dict
from collections import Counter

from agents.order import invoke_order_agent
from agents.complaint import invoke_complaint_agent
from agents.search import invoke_product_agent
from utils.logger import logger

IntentType = Literal["order", "complaint", "product"]

# -----------------------------
# 1️⃣ Keyword Configuration
# -----------------------------
ORDER_KEYWORDS = {
    "order", "track", "tracking", "delivery", "shipped",
    "shipment", "status", "where is my order", "awb"
}

COMPLAINT_KEYWORDS = {
    "complaint", "issue", "problem", "bad", "damaged",
    "broken", "refund", "return", "replace", "late",
    "not working", "poor", "wrong item", "cancel"
}

# -----------------------------
# 2️⃣ Regex Patterns
# -----------------------------
ORDER_ID_PATTERN = re.compile(
    r"(ord[-_]?\d+|#\d{4,}|\border\s?\d{3,})",
    re.IGNORECASE
)

# -----------------------------
# 3️⃣ Telemetry Counters
# -----------------------------
_intent_counter = Counter()

def get_intent_metrics() -> Dict[str, int]:
    """Expose routing metrics for monitoring."""
    return dict(_intent_counter)

# -----------------------------
# 4️⃣ Utility Functions
# -----------------------------
def normalize(text: str) -> str:
    return text.lower().strip()

def keyword_score(text: str, keywords: set) -> int:
    """Count keyword matches for confidence scoring."""
    return sum(1 for kw in keywords if kw in text)

def extract_order_id(text: str) -> str | None:
    """Extract order ID if present."""
    match = ORDER_ID_PATTERN.search(text)
    return match.group(0) if match else None

# -----------------------------
# 5️⃣ Main Routing Logic
# -----------------------------
def route_intent(user_id: str, user_input: str) -> Dict:
    """
    Route user input to the correct agent with memory integration.

    Returns:
    {
        "intent": "order|complaint|product",
        "confidence": "high|medium|low",
        "response": JSON dict from the agent,
        "order_id": str | None
    }
    """
    text = normalize(user_input)

    order_score = keyword_score(text, ORDER_KEYWORDS)
    complaint_score = keyword_score(text, COMPLAINT_KEYWORDS)
    order_id = extract_order_id(text)

    # -------------------------
    # Determine intent
    # -------------------------
    if complaint_score > 0:
        intent = "complaint"
        confidence = "high" if complaint_score > 1 else "medium"
    elif order_score > 0 or order_id:
        intent = "order"
        confidence = "high" if order_id else "medium"
    else:
        intent = "product"
        confidence = "low"

    _intent_counter[intent] += 1
    logger.info(f"IntentRouter → {intent} | confidence={confidence} | order_id={order_id}")

    # -------------------------
    # Route to appropriate agent
    # -------------------------
    try:
        if intent == "order":
            agent_response = invoke_order_agent(user_id, user_input, {"order_id": order_id} if order_id else None)
        elif intent == "complaint":
            agent_response = invoke_complaint_agent(user_id, user_input)
        else:
            agent_response = invoke_product_agent(user_id, user_input)

    except Exception as e:
        logger.error(f"Agent invocation failed: {e}")
        agent_response = {"message": "Sorry, we could not process your request. Please try again later."}

    return {
        "intent": intent,
        "confidence": confidence,
        "response": agent_response,
        "order_id": order_id
    }
