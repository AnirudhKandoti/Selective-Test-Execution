
SUPPORTED = {"USD", "EUR", "SEK"}

def is_supported_currency(code: str) -> bool:
    return code in SUPPORTED

# touch to trigger diff
