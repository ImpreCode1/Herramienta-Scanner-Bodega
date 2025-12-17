import re

INVOICE_PATTERNS = [
    r"No\.?\s*FAC[:\-]?\s*(\d{6,})",
    r"Ref\.?\s*Int[:\-]?\s*(\d{6,})",
    r"Factura\s*N[oº]?\s*[:\-]?\s*(\d{6,})"
]

def extract_invoice_number_from_text(text: str) -> str | None:
    for pattern in INVOICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
