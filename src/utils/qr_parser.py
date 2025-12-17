import re
from loguru import logger


def extract_invoice_number(raw_code: str) -> str | None:
    """
    Extrae el número de factura desde el texto leído del código de barras.
    Retorna un string limpio o None si no es válido.
    """

    if not raw_code:
        return None

    # Normalizar
    text = raw_code.strip()
    text = text.replace(" ", "").replace("\n", "")

    logger.debug(f"Código recibido: {text}")

    # Caso 1: NumFac explícito (DIAN)
    match = re.search(r"NumFac[:=]?(\d{5,})", text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Caso 2: número largo (más común)
    match = re.search(r"\b\d{8,}\b", text)
    if match:
        return match.group(0)

    # Caso 3: formato con guiones (ej: 206-581544)
    match = re.search(r"\b\d{3,}-\d{3,}\b", text)
    if match:
        return match.group(0).replace("-", "")

    logger.warning(f"No se pudo extraer número de factura: {raw_code}")
    return None
