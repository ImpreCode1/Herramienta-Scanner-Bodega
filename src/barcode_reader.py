import os
import sys
from pathlib import Path
from PIL import Image
from loguru import logger


# ==================================================
# Configuración ZBAR (CRÍTICO para PyInstaller)
# ==================================================
def setup_zbar():
    """
    Asegura que pyzbar pueda encontrar las DLLs de ZBar
    cuando la app está empaquetada con PyInstaller.
    """
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
        zbar_dir = base_dir / "runtime" / "zbar" / "bin"

        if zbar_dir.exists():
            os.environ["PATH"] = (
                str(zbar_dir)
                + os.pathsep
                + os.environ.get("PATH", "")
            )
        else:
            logger.error(f"Directorio ZBar no encontrado: {zbar_dir}")


# ⚠️ DEBE ejecutarse ANTES del import pyzbar
setup_zbar()

from pyzbar.pyzbar import decode


# ==================================================
# Lógica de negocio
# ==================================================
VALID_TYPES = {"CODE128", "CODE39"}


def is_valid_invoice_code(text: str) -> bool:
    return (
        text.isdigit() and
        10 <= len(text) <= 12
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
