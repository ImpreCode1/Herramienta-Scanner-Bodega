from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add(LOG_DIR / "scanner.log", level="DEBUG", rotation="1 MB")

__all__ = ["logger"]
