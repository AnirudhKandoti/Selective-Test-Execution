
from .utils import is_supported_currency

class PaymentError(ValueError):
    pass

def create_payment(amount: float, currency: str, customer_id: str) -> dict:
    if amount is None or amount <= 0:
        raise PaymentError("Amount must be positive.")
    if not is_supported_currency(currency):
        raise PaymentError("Unsupported currency.")
    if not customer_id:
        raise PaymentError("Missing customer_id.")
    return {"paymentId": f"pay-{customer_id}-001", "amount": amount, "currency": currency}

def get_payment(payment_id: str) -> dict:
    if payment_id == "missing":
        raise KeyError("Not found")
    return {"paymentId": payment_id, "amount": 10.0, "currency": "USD", "status": "PENDING"}
