from PySide6.QtCore import QThread, Signal
from pathlib import Path
from collections import defaultdict
import re
from loguru import logger

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
        self._loguru_id = None

    def stop(self):
        self._is_running = False

    # 🔗 Sink de loguru → UI
    def _loguru_sink(self, message):
        self.log.emit(message.rstrip())

    def run(self):
        try:
            # =====================================================
            # CONECTAR LOGURU AL WORKER
            # =====================================================
            self._loguru_id = logger.add(
                self._loguru_sink,
                level="INFO",
                format="{message}"
            )

            # -------------------------------
            # FASE 1: PDF -> IMÁGENES (0–25%)
            # -------------------------------
            self.log.emit("📄 Convirtiendo PDF a imágenes…")
            self.progress.emit(5)

            images = pdf_to_images(self.pdf_path)
            total_pages = len(images)

            if total_pages == 0:
                raise ValueError("El PDF no contiene páginas")

            self.progress.emit(25)
            self.log.emit(f"✅ {total_pages} páginas convertidas exitosamente")

            # -------------------------------
            # FASE 2: DETECCIÓN (25–50%)
            # -------------------------------
            self.log.emit("🔍 Analizando códigos de barras en todas las páginas…")
            self.progress.emit(30)

            documents, report = split_by_barcode(images)

            total_docs = len(documents)
            docs_without_code = report.get("documents_without_code", 0)

            self.progress.emit(50)
            self.log.emit("📊 Resumen de detección:")
            self.log.emit(f"   • Facturas detectadas: {total_docs}")
            self.log.emit(f"   • Páginas sin código: {docs_without_code}")

            if total_docs == 0:
                self.log.emit("⚠️ No se detectaron documentos con código de barras")
                self.progress.emit(100)
                return

            # -------------------------------
            # FASE 3: GENERACIÓN DE PDFs (50–100%)
            # -------------------------------
            self.log.emit("")
            self.log.emit("📝 Generando archivos PDF individuales…")
            self.log.emit("─" * 50)

            counters = defaultdict(int)
            processed_docs = 0

            for code, imgs in documents.items():
                if not self._is_running:
                    self.log.emit("")
                    self.log.emit("⛔ Proceso cancelado por el usuario")
                    return

                safe_code = safe_filename(code)
                counters[safe_code] += 1
                suffix = f"_{counters[safe_code]}" if counters[safe_code] > 1 else ""
                filename = f"{safe_code}{suffix}.pdf"

                save_pdf(imgs, self.output_dir / filename)

                num_pages = len(imgs)
                page_text = "página" if num_pages == 1 else "páginas"

                self.log.emit(f"📄 Factura: {code}")
                self.log.emit(f"   └─ {num_pages} {page_text} → {filename}")

                processed_docs += 1
                progress_value = 50 + int((processed_docs / total_docs) * 50)
                self.progress.emit(progress_value)

            # -------------------------------
            # FINAL
            # -------------------------------
            self.log.emit("─" * 50)
            self.log.emit("")
            self.log.emit("✨ Resumen final:")
            self.log.emit(f"   • Total de facturas generadas: {total_docs}")
            self.log.emit(f"   • Páginas sin código detectado: {docs_without_code}")
            self.log.emit(f"   • Ubicación: {self.output_dir}")

            self.progress.emit(100)
            self.log.emit("")
            self.log.emit("✔️ Procesamiento completado exitosamente")

        except Exception as e:
            self.log.emit("")
            self.log.emit(f"❌ Error crítico: {str(e)}")

            import traceback
            self.log.emit("📋 Detalles técnicos:")
            for line in traceback.format_exc().split("\n"):
                if line.strip():
                    self.log.emit(f"   {line}")

        finally:
            # 🧹 Limpiar sink de loguru
            if self._loguru_id is not None:
                logger.remove(self._loguru_id)

            self.finished.emit()
