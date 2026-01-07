"""
create_ticket.py
----------------
Handles complaint ticket creation for the e-commerce tri-agent system.
Deterministic: always generates a unique ticket ID and timestamped ticket info.
"""
import sys
import os
import uuid
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger

# Allowed ticket statuses
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed", "rejected"]

def create_complaint_ticket(user_input: str, user_id: str | None = None) -> dict:
    """Create a new complaint ticket with status 'open'."""
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    created_at = datetime.utcnow().isoformat() + "Z"

    ticket_info = {
        "ticket_id": ticket_id,
        "user_id": user_id or "anonymous",
        "created_at": created_at,
        "complaint_summary": user_input[:200],
        "status": "open"
    }

    logger.info(f"Complaint ticket created: {ticket_id}")
    return ticket_info


def update_ticket_status(ticket_info: dict, new_status: str) -> dict:
    """
    Update the status of an existing ticket.
    
    Args:
        ticket_info (dict): Existing ticket data.
        new_status (str): One of TICKET_STATUSES.
    
    Returns:
        dict: Updated ticket data.
    """
    if new_status not in TICKET_STATUSES:
        raise ValueError(f"Invalid status '{new_status}', must be one of {TICKET_STATUSES}")
    
    ticket_info["status"] = new_status
    ticket_info["updated_at"] = datetime.utcnow().isoformat() + "Z"
    logger.info(f"Ticket {ticket_info['ticket_id']} status updated to '{new_status}'")
    return ticket_info


# Optional self-test
if __name__ == "__main__":
    ticket = create_complaint_ticket("Package was damaged upon delivery", user_id="user123")
    print(ticket)

    ticket = update_ticket_status(ticket, "in_progress")
    print(ticket)

    ticket = update_ticket_status(ticket, "resolved")
    print(ticket)