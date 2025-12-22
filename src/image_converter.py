from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
from pathlib import Path
from loguru import logger
import sys
import os

from utils.runtime import poppler_bin


def pdf_to_images(pdf_path: str, dpi: int = 300):
    logger.info(f"Convirtiendo PDF a imágenes: {pdf_path}")

    poppler_path = poppler_bin()

    if not poppler_path.exists():
        raise RuntimeError(
            f"Poppler no encontrado en {poppler_path}"
        )

    # En Windows, configurar variable de entorno para ocultar consolas
    # de subprocesos hijos
    old_startupinfo = None
    if sys.platform == 'win32':
        # Esto funciona a nivel de sistema operativo
        import subprocess
        
        # Crear STARTUPINFO para ocultar ventanas
        if hasattr(subprocess, 'STARTUPINFO'):
            old_startupinfo = getattr(subprocess, '_default_startupinfo', None)
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Monkey patch temporal solo para esta función
            _original_popen_init = subprocess.Popen.__init__
            
            def _popen_init_hidden(self, *args, **kwargs):
                if 'startupinfo' not in kwargs:
                    kwargs['startupinfo'] = startupinfo
                if 'creationflags' not in kwargs:
                    kwargs['creationflags'] = 0
                kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
                return _original_popen_init(self, *args, **kwargs)
            
            subprocess.Popen.__init__ = _popen_init_hidden

    try:
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            poppler_path=str(poppler_path)
        )
        logger.info(f"Páginas convertidas: {len(images)}")
        return images
    finally:
        # Restaurar
        if sys.platform == 'win32' and old_startupinfo is not None:
            subprocess.Popen.__init__ = _original_popen_init