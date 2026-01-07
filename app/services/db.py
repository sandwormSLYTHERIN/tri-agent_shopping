# services/db.py

from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import logger


class InMemoryDB:
    """
    Simple in-memory database for products, orders, and tickets.
    Replace with real DB (Postgres, Mongo, etc.) in production.
    """

    def __init__(self):
        self.products: Dict[str, dict] = {}  # product_id -> product info
        self.orders: Dict[str, dict] = {}    # order_id -> order info
        self.tickets: Dict[str, dict] = {}   # ticket_id -> ticket info

    # -----------------------------
    # Product Methods
    # -----------------------------
    def add_product(self, product: dict):
        product_id = product["id"]
        self.products[product_id] = product
        logger.info(f"Product added: {product_id}")

    def get_product(self, product_id: str) -> Optional[dict]:
        return self.products.get(product_id)

    def get_all_products(self) -> List[dict]:
        return list(self.products.values())

    # -----------------------------
    # Order Methods
    # -----------------------------
    def add_order(self, order: dict):
        order_id = order["order_id"]
        self.orders[order_id] = order
        logger.info(f"Order added: {order_id}")

    def get_order(self, order_id: str) -> Optional[dict]:
        return self.orders.get(order_id)

    def update_order_status(self, order_id: str, status: str):
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            self.orders[order_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            logger.info(f"Order {order_id} status updated to {status}")
            return self.orders[order_id]
        logger.warning(f"Order {order_id} not found")
        return None

    # -----------------------------
    # Ticket Methods
    # -----------------------------
    def add_ticket(self, ticket: dict):
        ticket_id = ticket["ticket_id"]
        self.tickets[ticket_id] = ticket
        logger.info(f"Ticket added: {ticket_id}")

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        return self.tickets.get(ticket_id)

    def update_ticket_status(self, ticket_id: str, status: str):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            self.tickets[ticket_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            logger.info(f"Ticket {ticket_id} status updated to {status}")
            return self.tickets[ticket_id]
        logger.warning(f"Ticket {ticket_id} not found")
        return None


# -----------------------------
# Singleton instance
# -----------------------------
db_instance = InMemoryDB()


# -----------------------------
# Convenience functions
# -----------------------------
def add_product(product: dict):
    return db_instance.add_product(product)


def get_product(product_id: str):
    return db_instance.get_product(product_id)


def get_all_products():
    return db_instance.get_all_products()


def add_order(order: dict):
    return db_instance.add_order(order)


def get_order(order_id: str):
    return db_instance.get_order(order_id)


def update_order_status(order_id: str, status: str):
    return db_instance.update_order_status(order_id, status)


def add_ticket(ticket: dict):
    return db_instance.add_ticket(ticket)


def get_ticket(ticket_id: str):
    return db_instance.get_ticket(ticket_id)


def update_ticket_status(ticket_id: str, status: str):
    return db_instance.update_ticket_status(ticket_id, status)
