from pathlib import Path
import sys
import os


# ==================================================
# Utilidad base para rutas en runtime (PyInstaller)
# ==================================================
def runtime_path(relative: str) -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / relative
    return Path(relative)


# ==================================================
# TESSERACT
# ==================================================
def tesseract_cmd() -> Path:
    return runtime_path("runtime/tesseract/tesseract.exe")


def tessdata_dir() -> Path:
    return runtime_path("runtime/tesseract/tessdata")


# ==================================================
# POPPLER
# ==================================================
def poppler_bin() -> Path:
    return runtime_path("runtime/poppler/Library/bin")


# ==================================================
# ZBAR (CRÍTICO)
# ==================================================
def zbar_bin() -> Path:
    return runtime_path("runtime/zbar/bin")


def setup_zbar_path():
    """
    Inyecta ZBar en el PATH para que pyzbar + ctypes
    puedan encontrar libzbar y libiconv.
    """
    zbar_path = zbar_bin()

    if zbar_path.exists():
        os.environ["PATH"] = (
            str(zbar_path)
            + os.pathsep
            + os.environ.get("PATH", "")
        )
    else:
        print(f"[WARN] ZBar no encontrado en {zbar_path}")
