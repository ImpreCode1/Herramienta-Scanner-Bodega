from pyzbar.pyzbar import decode
from PIL import Image
from loguru import logger

VALID_TYPES = {"CODE128", "CODE39"}

def is_valid_invoice_code(text: str) -> bool:
    return (
        text.isdigit() and
        8 <= len(text) <= 12
    )

def read_barcode(image: Image.Image) -> str | None:
    width, height = image.size
    barcodes = decode(image)

    candidates = []

    for barcode in barcodes:
        barcode_type = barcode.type.upper()
        raw_text = barcode.data.decode("utf-8", errors="ignore").strip()

        if barcode_type not in VALID_TYPES:
            continue

        if not is_valid_invoice_code(raw_text):
            continue

        # Posición del código
        x, y, w, h = barcode.rect
        vertical_ratio = y / height  # 0 = arriba, 1 = abajo

        candidates.append((vertical_ratio, raw_text))

    if not candidates:
        return None

    # Priorizar el más arriba en la página
    candidates.sort(key=lambda x: x[0])

    selected = candidates[0][1]
    logger.info(f"Código de factura seleccionado: {selected}")
    return selected
