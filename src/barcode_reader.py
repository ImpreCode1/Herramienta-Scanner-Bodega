import cv2
import numpy as np
from PIL import Image
from loguru import logger
from typing import Any, Tuple, cast

VALID_MIN_LEN = 10
VALID_MAX_LEN = 13


def is_valid_invoice_code(text: str) -> bool:
    return text.isdigit() and VALID_MIN_LEN <= len(text) <= VALID_MAX_LEN


def read_barcode(image: Image.Image) -> str | None:
    try:
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        detector = cv2.barcode.BarcodeDetector()  # type: ignore[attr-defined]

        result = cast(
            Tuple[Any, ...],
            detector.detectAndDecode(cv_img)
        )

        if len(result) == 4:
            _, decoded_text, _, _ = result
        else:
            decoded_text, _, _ = result

        if not decoded_text:
            return None

        decoded_text = str(decoded_text).strip()

        if is_valid_invoice_code(decoded_text):
            logger.info(f"Código de factura detectado: {decoded_text}")
            return decoded_text

        return None

    except Exception as e:
        logger.error(f"Error leyendo barcode con OpenCV: {e}")
        return None
