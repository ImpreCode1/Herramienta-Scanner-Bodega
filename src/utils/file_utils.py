import re
from pathlib import Path
from loguru import logger

def sanitize_filename(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\-\.]", "_", text)
    return text

def save_pdf(images, output_path: Path):
    if not images:
        return

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:]
    )

    logger.info(f"PDF generado: {output_path.name}")
