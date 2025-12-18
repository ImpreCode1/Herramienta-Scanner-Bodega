from PySide6.QtCore import QThread, Signal
from pathlib import Path
from collections import defaultdict
import re

from image_converter import pdf_to_images
from pdf_processor import split_by_barcode
from utils.file_utils import save_pdf


def safe_filename(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[<>:\"/\\|?*\n\r\t]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:150]


class ScannerWorker(QThread):
    log = Signal(str)
    progress = Signal(int)
    finished = Signal()

    def __init__(self, pdf_path, output_dir):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            # -------------------------------
            # FASE 1: PDF -> IMÁGENES (0-30%)
            # -------------------------------
            self.log.emit("📄 Convirtiendo PDF a imágenes…")
            images = pdf_to_images(self.pdf_path)
            total_pages = len(images)

            if total_pages == 0:
                raise ValueError("El PDF no contiene páginas")

            self.progress.emit(30)
            self.log.emit(f"📑 Páginas convertidas: {total_pages}")

            # -------------------------------
            # FASE 2: DETECCIÓN Y GENERACIÓN
            # -------------------------------
            self.log.emit("🔍 Detectando códigos de barras…")
            documents, report = split_by_barcode(images)

            total_docs = len(documents)
            if total_docs == 0:
                self.log.emit("⚠️ No se detectaron documentos con código")
                self.progress.emit(100)
                self.finished.emit()
                return

            counters = defaultdict(int)
            processed_docs = 0

            for code, imgs in documents.items():
                if not self._is_running:
                    self.log.emit("⛔ Proceso cancelado por el usuario")
                    return

                safe_code = safe_filename(code)
                counters[safe_code] += 1

                suffix = f"_{counters[safe_code]}" if counters[safe_code] > 1 else ""
                filename = f"{safe_code}{suffix}.pdf"

                save_pdf(imgs, self.output_dir / filename)
                self.log.emit(f"✅ PDF generado: {filename}")

                processed_docs += 1
                progress_value = 30 + int((processed_docs / total_docs) * 70)
                self.progress.emit(progress_value)

            # -------------------------------
            # FINAL
            # -------------------------------
            self.log.emit(f"📊 Facturas sin código: {report['documents_without_code']}")
            self.progress.emit(100)
            self.log.emit("✔️ Procesamiento finalizado")

        except Exception as e:
            self.log.emit(f"❌ Error: {e}")

        self.finished.emit()
