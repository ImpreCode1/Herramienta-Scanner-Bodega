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
# OCULTAR CONSOLAS DE SUBPROCESOS (Windows)
# ==================================================
def hide_subprocess_consoles():
    """
    Configura subprocess para que no muestre ventanas de consola
    en Windows cuando se ejecuten comandos externos como tesseract o poppler.
    
    IMPORTANTE: Debe llamarse DESPUÉS de todas las importaciones principales
    para evitar conflictos con asyncio en Python 3.13+
    """
    if sys.platform == 'win32':
        import subprocess
        
        # Verificar que no hayamos hecho esto ya
        if hasattr(subprocess.run, '_no_window_wrapped'):
            return
        
        _original_run = subprocess.run
        _original_popen = subprocess.Popen
        
        def _run_no_window(*args, **kwargs):
            kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
            return _original_run(*args, **kwargs)
        
        def _popen_no_window(*args, **kwargs):
            kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
            return _original_popen(*args, **kwargs)
        
        # Marcar como wrapped para evitar doble wrapping
        _run_no_window._no_window_wrapped = True
        _popen_no_window._no_window_wrapped = True
        
        subprocess.run = _run_no_window
        subprocess.Popen = _popen_no_window
