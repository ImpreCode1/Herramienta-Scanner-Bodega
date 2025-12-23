import re

# =========================
# No. Fac / Factura No
# =========================
INVOICE_NUMBER_PATTERNS = [
    r"No\.?\s*FAC\.?\s*[:\-]?\s*(\d{10,})",
    r"Factura\s*N[oº]?\s*[:\-]?\s*(\d{10,})",
]

def extract_invoice_number_from_text(text: str) -> str | None:
    for pattern in INVOICE_NUMBER_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


# =========================
# Ref.Int.
# =========================
REF_INT_PATTERNS = [
    r"Ref\.?\s*Int\.?\s*[:\-]?\s*(\d{10,})",
]

def extract_ref_int_from_text(text: str) -> str | None:
    for pattern in REF_INT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
