from pdf2image import convert_from_path
from pathlib import Path
from loguru import logger

def pdf_to_images(pdf_path: str, dpi: int = 300):
    logger.info(f"Convirtiendo PDF a imágenes: {pdf_path}")

    images = convert_from_path(pdf_path, dpi=dpi)

    logger.info(f"Páginas convertidas: {len(images)}")
    return images
