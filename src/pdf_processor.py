import re
from collections import defaultdict
from pathlib import Path
from loguru import logger
import pytesseract
from pytesseract import image_to_string

from barcode_reader import read_barcode
from invoice_text_parser import extract_invoice_number_from_text, extract_ref_int_from_text
from utils.image_preprocessor import preprocess_for_ocr
from utils.runtime import tesseract_cmd


# =========================
# Configuración Tesseract (PORTABLE)
# =========================
_TESSERACT = tesseract_cmd()

if _TESSERACT.exists():
    pytesseract.pytesseract.tesseract_cmd = str(_TESSERACT)
else:
    logger.warning(f"Tesseract no encontrado en {_TESSERACT}")


# =========================
# Utilidades
# =========================
def extract_page_number(text: str) -> int | None:
    """
    Extrae el número de página de la forma 'Pág. X de Y'.
    """
    match = re.search(r"Pág\.\s*(\d+)\s*de", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


# =========================
# Lógica principal
# =========================
def split_by_barcode(images):
    documents = defaultdict(list)

    report = {
        "total_pages": 0,
        "documents_with_code": 0,
        "documents_without_code": 0,
        "errors": []
    }

    current_code = None

    for idx, image in enumerate(images, start=1):
        report["total_pages"] += 1

        page_number = None
        detected_code = None

        try:
            # 1️⃣ Intentar leer código de barras
            detected_code = read_barcode(image)

            if detected_code:
                detected_code = str(detected_code).strip()

            # 2️⃣ OCR solo si barcode no es confiable
            if not detected_code or len(detected_code) < 6:
                try:
                    width, height = image.size

                    # =========================
                    # 2️⃣ OCR PARTE SUPERIOR → Ref.Int.
                    # =========================
                    top_crop = image.crop((
                        0,
                        0,
                        width,
                        int(height * 0.35)
                    ))

                    processed_top = preprocess_for_ocr(top_crop)

                    text_top = image_to_string(
                        processed_top,
                        lang="eng",
                        config="--psm 6"
                    )

                    detected_code = extract_ref_int_from_text(text_top)

                    # =========================
                    # 3️⃣ OCR PARTE INFERIOR → No. Fac.
                    # =========================
                    if not detected_code:
                        bottom_crop = image.crop((
                            0,
                            int(height * 0.65),
                            width,
                            height
                        ))

                        processed_bottom = preprocess_for_ocr(bottom_crop)

                        text_bottom = image_to_string(
                            processed_bottom,
                            lang="eng",
                            config="--psm 6"
                        )

                        page_number = extract_page_number(text_bottom)
                        detected_code = extract_invoice_number_from_text(text_bottom)

                except Exception as e:
                    logger.error(f"OCR falló en página {idx}: {e}")
                    detected_code = None


            # 3️⃣ Resolver documento actual
            if detected_code:
                current_code = str(detected_code)
                report["documents_with_code"] += 1
                logger.info(
                    f"Página {idx}: factura detectada -> {current_code}"
                )
            else:
                if not current_code:
                    current_code = "SIN_CODIGO"
                report["documents_without_code"] += 1

            documents[current_code].append((page_number, image))

        except Exception as e:
            logger.error(f"Error en página {idx}: {e}")
            report["errors"].append(str(e))
            documents["ERROR"].append((None, image))

    # =========================
    # Ordenar páginas
    # =========================
    for code in documents:
        documents[code].sort(
            key=lambda x: x[0] if x[0] is not None else 9999
        )

    return documents, report
