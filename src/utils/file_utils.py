import re
from pathlib import Path
from loguru import logger
from PIL import Image

def sanitize_filename(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\-\.]", "_", text)
    return text

def process_image_for_pdf(img: Image.Image, max_width=1240, max_height=1754, quality=60) -> Image.Image:
    """
    Ajusta la imagen para PDF de facturas escaneadas:
    - Convierte a grayscale (blanco y negro)
    - Redimensiona manteniendo proporción
    - Comprueba que sea JPEG-friendly
    """
    img = img.convert("L")  # grayscale
    img.thumbnail((max_width, max_height))
    return img

def save_pdf(images_with_meta, output_path: Path, quality: int = 60):
    """
    Guarda un PDF optimizado desde una lista de imágenes escaneadas.
    """
    if not images_with_meta:
        logger.warning("No hay imágenes para generar PDF.")
        return
    
    processed_images = []
    for _, img in images_with_meta:
        processed = process_image_for_pdf(img, quality=quality)
        processed_images.append(processed)

    # Guardar PDF optimizado
    processed_images[0].save(
        output_path,
        save_all=True,
        append_images=processed_images[1:],
        format="PDF",
        quality=quality,
        optimize=True
    )

    logger.info(f"PDF optimizado generado: {output_path.name}")
