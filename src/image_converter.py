from pdf2image import convert_from_path
from pathlib import Path
from loguru import logger

from utils.runtime import poppler_bin


def pdf_to_images(pdf_path: str, dpi: int = 300):
    logger.info(f"Convirtiendo PDF a imágenes: {pdf_path}")

    poppler_path = poppler_bin()

    if not poppler_path.exists():
        raise RuntimeError(
            f"Poppler no encontrado en {poppler_path}"
        )

    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=str(poppler_path)
    )

    logger.info(f"Páginas convertidas: {len(images)}")
    return images
