# tools/order_lookup.py

from typing import Dict, Optional
from datetime import datetime
from utils.logger import logger


# -----------------------------
# Mock Order Database
# (Replace with real DB/API)
# -----------------------------

MOCK_ORDERS = {
    "ORD12345": {
        "order_id": "ORD12345",
        "status": "Shipped",
        "carrier": "BlueDart",
        "tracking_id": "BD789456123",
        "expected_delivery": "2025-01-05",
        "last_updated": "2025-01-02"
    },
    "ORD67890": {
        "order_id": "ORD67890",
        "status": "Delivered",
        "carrier": "Delhivery",
        "tracking_id": "DL456789321",
        "expected_delivery": "2024-12-28",
        "last_updated": "2024-12-28"
    }
}


# -----------------------------
# Tool Function
# -----------------------------

def get_order_status(order_context: Optional[Dict]) -> Dict:
    """
    Deterministically fetch order details.

    Input:
        order_context: {
            "order_id": str
        }

    Output:
        {
            "order_id": str,
            "status": str,
            "carrier": str,
            "tracking_id": str,
            "expected_delivery": str,
            "last_updated": str
        }
    """

    if not order_context or "order_id" not in order_context:
        logger.warning("Order lookup failed: missing order_id")
        return {
            "error": "ORDER_ID_MISSING",
            "message": "Order ID not provided"
        }

    order_id = order_context["order_id"]

    logger.info(f"Fetching order status for {order_id}")

    order = MOCK_ORDERS.get(order_id)

    if not order:
        logger.warning(f"Order not found: {order_id}")
        return {
            "error": "ORDER_NOT_FOUND",
            "order_id": order_id
        }

    return order
