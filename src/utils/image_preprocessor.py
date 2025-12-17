import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(pil_image: Image.Image) -> Image.Image:
    """
    Mejora contraste y binariza para OCR.
    """
    img = np.array(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )

    return Image.fromarray(processed)
