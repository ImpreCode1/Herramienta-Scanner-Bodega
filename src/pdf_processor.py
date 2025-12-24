import re
from collections import defaultdict, Counter
from pathlib import Path
from loguru import logger
from PIL import Image
from typing import List, Tuple, Dict, Optional

import pytesseract

from invoice_text_parser import extract_invoice_number_from_text, extract_ref_int_from_text
from utils.image_preprocessor import preprocess_for_ocr
from utils.runtime import tesseract_cmd
from extract_codes import extract_codes  # Tu primer script
from extract_qr_and_barcode import extract_qr_and_barcode  # Tu segundo script

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
def extract_page_number(text: str) -> Optional[int]:
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
def split_by_barcode(images: List[Image.Image]) -> Tuple[Dict[str, List[Tuple[Optional[int], Image.Image]]], Dict]:
    """
    Procesa cada página e intenta asignarla a un documento basado en QR, barcode o OCR.
    """
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

        logger.info(f"\n📄 Procesando página {idx}")

        try:
            # =========================
            # 1️⃣ Intento QR + Barcode (ZBar)
            # =========================
            numfac_qr, numfac_barcode = extract_qr_and_barcode(image)

            if numfac_qr:
                detected_code = numfac_qr
                logger.info(f"[QR] Detectado: {detected_code}")
            elif numfac_barcode:
                detected_code = numfac_barcode
                logger.info(f"[BARCODE] Detectado: {detected_code}")
            else:
                logger.info("[QR/BARCODE] No detectado")

            # =========================
            # 2️⃣ OCR (extract_codes)
            # =========================
            if not detected_code or len(detected_code) < 6:
                codes = extract_codes(image)

                # Tomamos el valor más común entre no_header, ref_int, no_fac
                candidates = [v for v in (codes.get("no_header"), codes.get("ref_int"), codes.get("no_fac")) if v]
                if candidates:
                    count = Counter(candidates)
                    detected_code = count.most_common(1)[0][0]
                    logger.info(f"[OCR-COMBINADO] Código más común extraído: {detected_code}")
                else:
                    # ---------- OCR TOP ----------
                    width, height = image.size
                    top_crop = image.crop((0, 0, width, int(height * 0.35)))
                    processed_top = preprocess_for_ocr(top_crop)
                    text_top = pytesseract.image_to_string(processed_top, lang="eng", config="--psm 6")
                    logger.debug("[OCR-TOP] Texto crudo:\n" + text_top[:500])

                    ref_int = extract_ref_int_from_text(text_top)
                    if ref_int:
                        detected_code = ref_int
                        logger.info(f"[OCR-TOP] Ref.Int extraída: {detected_code}")

                    # ---------- OCR BOTTOM ----------
                    if not detected_code:
                        bottom_crop = image.crop((0, int(height * 0.65), width, height))
                        processed_bottom = preprocess_for_ocr(bottom_crop)
                        text_bottom = pytesseract.image_to_string(processed_bottom, lang="eng", config="--psm 6")
                        logger.debug("[OCR-BOTTOM] Texto crudo:\n" + text_bottom[:500])

                        page_number = extract_page_number(text_bottom)
                        invoice_number = extract_invoice_number_from_text(text_bottom)
                        if invoice_number:
                            detected_code = invoice_number
                            logger.info(f"[OCR-BOTTOM] Página: {page_number}, Factura extraída: {detected_code}")

            # =========================
            # 3️⃣ Resolución final y asignación
            # =========================
            if detected_code:
                detected_code = str(detected_code).strip()
                current_code = detected_code
                report["documents_with_code"] += 1
                logger.success(f"✅ Página {idx}: Documento asignado a -> {current_code}")
            else:
                if not current_code:
                    current_code = "SIN_CODIGO"
                report["documents_without_code"] += 1
                logger.warning(f"⚠️ Página {idx}: Sin código, se asigna a -> {current_code}")

            documents[current_code].append((page_number, image))

        except Exception as e:
            logger.exception(f"❌ Error en página {idx}")
            report["errors"].append(str(e))
            documents["ERROR"].append((None, image))

    # =========================
    # Ordenar páginas dentro de cada documento
    # =========================
    for code in documents:
        documents[code].sort(key=lambda x: x[0] if x[0] is not None else 9999)

    return documents, report
