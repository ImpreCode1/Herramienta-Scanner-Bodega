import re
from collections import defaultdict
from loguru import logger
from barcode_reader import read_barcode
from utils.qr_parser import extract_invoice_number
from pytesseract import image_to_string
import pytesseract
from pathlib import Path

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)

def extract_page_number(text: str) -> int | None:
    """
    Extrae el número de página de la forma 'Pág. X de Y'.
    Retorna el número de página (X) o None si no se encuentra.
    """
    match = re.search(r"Pág\.\s*(\d+)\s*de", text)
    if match:
        return int(match.group(1))
    return None

def split_by_barcode(images):
    documents = defaultdict(list)

    report = {
        "total_pages": 0,
        "documents_with_code": 0,
        "documents_without_code": 0,
        "errors": []
    }

    current_code = "SIN_CODIGO"

    for idx, image in enumerate(images, start=1):
        report["total_pages"] += 1

        try:
            code = read_barcode(image)

            if code:
                current_code = str(code)
                report["documents_with_code"] += 1
                logger.info(f"Página {idx}: nuevo documento -> {current_code}")
            else:
                report["documents_without_code"] += 1

            documents[current_code].append(image)

        except Exception as e:
            logger.error(f"Error en página {idx}: {e}")
            report["errors"].append(str(e))
            documents["ERROR"].append(image)

    return documents, report
