import re
from pathlib import Path
from loguru import logger

def sanitize_filename(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\-\.]", "_", text)
    return text

def save_pdf(images_with_meta, output_path: Path):
    if not images_with_meta:
        return
    
    images = [img for _, img in images_with_meta]

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:]
    )

    logger.info(f"PDF generado: {output_path.name}")
