from PySide6.QtCore import QThread, Signal

class ScannerWorker(QThread):
    log = Signal(str)
    finished = Signal()

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        self.log.emit("Iniciando procesamiento...")
        self.log.emit(f"Procesando archivo: {self.pdf_path}")

        # 🔜 aquí luego va tu lógica real
        self.log.emit("Procesamiento finalizado ✔️")

        self.finished.emit()
