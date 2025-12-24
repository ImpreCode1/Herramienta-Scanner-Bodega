import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Optional, Dict

OCR_LANG = "eng"
OCR_CONFIG = "--psm 6"

# =========================
# REGEX SIMPLES Y ROBUSTOS
# =========================
NO_HEADER_REGEX = re.compile(
    r"No\.?\s*(\d{3}-\d{5,7})",
    re.IGNORECASE
)

REF_INT_REGEX = re.compile(
    r"Ref\.?\s*Int\.?\s*[:\-]?\s*(\d{8,13})",
    re.IGNORECASE
)

NO_FAC_REGEX = re.compile(
    r"No\.?\s*FAC\.?\s*[:\-]?\s*(\d{8,13})",
    re.IGNORECASE
)

# =========================
# OCR HELPERS
# =========================
def normalize_ocr(text: str) -> str:
    """
    Normaliza errores comunes SOLO en etiquetas
    """
    fixes = {
        "N0.": "No.",
        "N0 ": "No ",
        "Ref.1nt": "Ref.Int",
        "1nt.": "Int.",
        "FAC": "FAC",
    }

    for wrong, right in fixes.items():
        text = text.replace(wrong, right)

    return text

def normalize_no_header(no_header: Optional[str]) -> Optional[str]:
    if not no_header:
        return None
    return no_header.replace("-", "0")

def preprocess(img: Image.Image) -> Image.Image:
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    return Image.fromarray(gray)

def ocr(img: Image.Image) -> str:
    return normalize_ocr(
        pytesseract.image_to_string(
            img,
            lang=OCR_LANG,
            config=OCR_CONFIG
        )
    )

# =========================
# EXTRACCIÓN PRINCIPAL
# =========================
def extract_codes(image: Image.Image) -> Dict[str, Optional[str]]:
    """
    Extrae los códigos: no_header, ref_int, no_fac de una imagen de factura.
    """
    w, h = image.size

    # =========================
    # CROP HEADER (No. + Ref.Int.)
    # =========================
    header_no_box = (
        int(w * 0.70),
        int(h * 0.06),
        int(w * 0.98),
        int(h * 0.13),
    )
    header_crop = image.crop(header_no_box)
    header_text = ocr(preprocess(header_crop))

    # =========================
    # CROP NO. FAC
    # =========================
    no_fac_box = (
        int(w * 0.25),
        int(h * 0.85),
        int(w * 0.50),
        int(h * 0.93),
    )
    no_fac_crop = image.crop(no_fac_box)
    no_fac_text = ocr(preprocess(no_fac_crop))

    # =========================
    # EXTRACCIÓN POR REGEX
    # =========================
    no_header = None
    ref_int = None
    no_fac = None

    m = NO_HEADER_REGEX.search(header_text)
    if m:
        no_header = normalize_no_header(m.group(1))

    m = REF_INT_REGEX.search(header_text)
    if m:
        ref_int = m.group(1)

    m = NO_FAC_REGEX.search(no_fac_text)
    if m:
        no_fac = m.group(1)

    return {
        "no_header": no_header,
        "ref_int": ref_int,
        "no_fac": no_fac,
    }

# =========================
# OPCIONAL: Helper para PDFs
# =========================
def extract_codes_from_pdf(pdf_path: str, page: int = 0) -> Dict[str, Optional[str]]:
    """
    Extrae códigos de la primera página (por defecto) de un PDF.
    """
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path, dpi=300)
    return extract_codes(images[page])
