from loguru import logger
import sys
from pathlib import Path


def get_base_dir():
    """
    Directorio base seguro para dev y exe (PyInstaller)
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_DIR = get_base_dir()
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 🔴 Quitar handlers por defecto
logger.remove()

# ✅ Log SIEMPRE a archivo
logger.add(
    LOG_DIR / "scanner.log",
    level="DEBUG",
    rotation="1 MB",
    retention="7 days",
    encoding="utf-8"
)

# ✅ Log a consola SOLO en desarrollo
if not getattr(sys, "frozen", False):
    logger.add(sys.stderr, level="INFO")

__all__ = ["logger"]
