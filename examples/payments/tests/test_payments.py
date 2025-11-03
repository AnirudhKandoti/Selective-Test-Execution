
import pytest
from examples.payments.app.payments import create_payment, get_payment, PaymentError

def test_create_payment_success():
    res = create_payment(12.5, "USD", "cust-1")
    assert res["paymentId"].startswith("pay-")
    assert res["amount"] == 12.5

def test_create_payment_invalid_amount():
    with pytest.raises(PaymentError):
        create_payment(-1, "USD", "cust-1")

def test_create_payment_unsupported_currency():
    with pytest.raises(PaymentError):
        create_payment(10, "ZZZ", "cust-1")

def test_get_payment_ok():
    res = get_payment("pay-abc")
    assert res["paymentId"] == "pay-abc"

def test_get_payment_missing():
    with pytest.raises(KeyError):
        get_payment("missing")
