from pathlib import Path
import sys

def runtime_path(relative):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / relative
    return Path(relative)

def tesseract_cmd():
    return runtime_path("runtime/tesseract/tesseract.exe")

def poppler_bin():
    return runtime_path("runtime/poppler/Library/bin")