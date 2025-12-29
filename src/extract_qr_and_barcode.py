import subprocess
import sys
import os
import re
import tempfile
from PIL import Image
from typing import Optional, Tuple, List

# =========================
# PATH RESOLVER
# =========================
def resource_path(relative: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative)
    return os.path.abspath(relative)

ZBAR_EXE = resource_path("runtime/zbar/bin/zbarimg.exe")

# =========================
# REGEX PARA QR
# =========================
NUMFAC_REGEX = re.compile(r"NumFac\s*:\s*([0-9\-]+)", re.IGNORECASE)

# =========================
# ZBAR RUNNER
# =========================
def run_zbar(image_path: str) -> List[str]:
    image_path = os.path.abspath(image_path)
    result = subprocess.run(
        [ZBAR_EXE, "--raw", image_path],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if not result.stdout.strip():
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

# =========================
# CROP DEFINITIVOS
# =========================
def crop_qr_zone(image: Image.Image) -> Image.Image:
    w, h = image.size
    box = (
        int(w * 0.05),
        int(h * 0.8),
        int(w * 0.3),
        int(h * 0.98),
    )
    return image.crop(box).convert("RGB")

def crop_barcode_zone(image: Image.Image) -> Image.Image:
    w, h = image.size
    box = (
        int(w * 0.25),
        int(h * 0.85),
        int(w * 0.56),
        int(h * 0.93),
    )
    return image.crop(box).convert("RGB")

# =========================
# EXTRAER NUMFAC DEL QR
# =========================
def extract_numfac_from_lines(lines: List[str]) -> Optional[str]:
    full_text = "\n".join(lines)
    m = NUMFAC_REGEX.search(full_text)
    if m:
        numfac = m.group(1).replace(" ", "").replace("-", "0")
        return numfac
    return None

# =========================
# FUNCION PRINCIPAL
# =========================
def extract_qr_and_barcode(image: Image.Image) -> Tuple[Optional[str], Optional[str]]:
    """
    Retorna una tupla: (numfac_qr, numfac_barcode)
    """
    # Procesamos QR
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = os.path.abspath(tmp.name)
        crop_qr_zone(image).save(temp_path)
    qr_lines = run_zbar(temp_path)
    os.remove(temp_path)
    numfac_qr = extract_numfac_from_lines(qr_lines) if qr_lines else None

    # Procesamos Barcode
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = os.path.abspath(tmp.name)
        crop_barcode_zone(image).save(temp_path)
    barcode_lines = run_zbar(temp_path)
    os.remove(temp_path)
    numfac_barcode = barcode_lines[0] if barcode_lines else None

    return numfac_qr, numfac_barcode
