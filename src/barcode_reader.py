from pyzbar.pyzbar import decode
from PIL import Image
from loguru import logger

VALID_TYPES = {
    "CODE128",
    "CODE39",
    "EAN13",
    "EAN8",
    "UPCA",
    "UPCE"
}

def read_barcode(image: Image.Image) -> str | None:
    barcodes = decode(image)

    if not barcodes:
        return None

    for barcode in barcodes:
        barcode_type = barcode.type.upper()
        raw_text = barcode.data.decode("utf-8", errors="ignore").strip()

        # ❌ Ignorar QR
        if barcode_type == "QRCODE":
            logger.debug("QR ignorado")
            continue

        # ❌ Ignorar tipos no deseados
        if barcode_type not in VALID_TYPES:
            logger.debug(f"Tipo ignorado: {barcode_type}")
            continue

        # ❌ Ignorar textos largos o multilínea
        if len(raw_text) > 40 or "\n" in raw_text:
            logger.debug("Código descartado por longitud/formato")
            continue

        logger.info(f"Código válido detectado [{barcode_type}]: {raw_text}")
        return raw_text

    return None
