
from examples.payments.app.utils import is_supported_currency

def test_supported_currency_true():
    assert is_supported_currency("USD")

def test_supported_currency_false():
    assert not is_supported_currency("INR")
