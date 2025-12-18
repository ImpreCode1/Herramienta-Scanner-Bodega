from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QFileDialog, QProgressBar,
    QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

from ui.worker import ScannerWorker
from pathlib import Path
import sys


# ==================================================
# Utilidad para PyInstaller
# ==================================================
def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", None)
    return Path(base) / relative_path if base else Path(relative_path)


# ==================================================
# Main Window
# ==================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Herramienta Scanner – Bodega")
        self.resize(800, 520)
        self.setWindowIcon(QIcon(str(resource_path("src/assets/logo_impresistem.png"))))

        # ---------------- HEADER ----------------
        logo = QLabel()
        pixmap = QPixmap(str(resource_path("src/assets/logo_impresistem.png")))
        logo.setPixmap(pixmap.scaled(
            110, 110,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

        title = QLabel("Scanner de Facturas")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        subtitle = QLabel("Separación automática por códigos de barras")
        subtitle.setStyleSheet("color: #475569;")

        text_layout = QVBoxLayout()
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        # ---------------- BOTONES ----------------
        self.btn_select = QPushButton("Seleccionar PDF")
        self.btn_select_output = QPushButton("Carpeta de salida")
        self.btn_process = QPushButton("Procesar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_process.setEnabled(False)
        self.btn_cancel.setEnabled(False)

        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)

        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:disabled {
                background-color: #fca5a5;
            }
        """)

        self.btn_select.setStyleSheet("padding: 6px 12px;")
        self.btn_select_output.setStyleSheet("padding: 6px 12px;")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_select)
        buttons_layout.addWidget(self.btn_select_output)
        buttons_layout.addWidget(self.btn_process)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.setSpacing(10)

        # ---------------- INFO ----------------
        self.info_label = QLabel("📄 Archivo: —   |   📁 Salida: —")
        self.info_label.setStyleSheet("color: #475569; font-size: 11px;")

        # ---------------- LOG ----------------
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #e5e7eb;
                font-family: Consolas;
                font-size: 11px;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        # ---------------- PROGRESO ----------------
        self.status_label = QLabel("Listo para procesar")
        self.status_label.setStyleSheet("color: #334155;")

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5f5;
                border-radius: 6px;
                height: 20px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 6px;
            }
        """)

        # ---------------- LAYOUT PRINCIPAL ----------------
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.log_area)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress)

        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # ---------------- ESTADO ----------------
        self.selected_pdf = None
        self.output_dir = None
        self.worker = None

        # ---------------- SEÑALES ----------------
        self.btn_select.clicked.connect(self.select_pdf)
        self.btn_select_output.clicked.connect(self.select_output_dir)
        self.btn_process.clicked.connect(self.process_pdf)
        self.btn_cancel.clicked.connect(self.cancel_process)

    # ==================================================
    # Selección de PDF
    # ==================================================
    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo PDF", "", "Archivos PDF (*.pdf)"
        )

        if file_path:
            self.selected_pdf = file_path
            self.log_area.append(f"📄 PDF seleccionado: {file_path}")
            self._update_info()
            self._update_process_state()

    # ==================================================
    # Selección carpeta salida
    # ==================================================
    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de salida"
        )

        if directory:
            self.output_dir = directory
            self.log_area.append(f"📁 Carpeta de salida: {directory}")
            self._update_info()
            self._update_process_state()

    # ==================================================
    def _update_info(self):
        pdf = Path(self.selected_pdf).name if self.selected_pdf else "—"
        out = self.output_dir if self.output_dir else "—"
        self.info_label.setText(f"📄 Archivo: {pdf}   |   📁 Salida: {out}")

    def _update_process_state(self):
        self.btn_process.setEnabled(bool(self.selected_pdf and self.output_dir))

    # ==================================================
    # Procesar
    # ==================================================
    def process_pdf(self):
        self.btn_process.setEnabled(False)
        self.btn_select.setEnabled(False)
        self.btn_select_output.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText("Procesando…")

        self.worker = ScannerWorker(self.selected_pdf, self.output_dir)
        self.worker.log.connect(self._append_log)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    # ==================================================
    # Cancelar
    # ==================================================
    def cancel_process(self):
        if self.worker and self.worker.isRunning():
            self.log_area.append("⛔ Cancelando proceso…")
            self.worker.stop()
            self.status_label.setText("Proceso cancelado")
            self.btn_cancel.setEnabled(False)

    # ==================================================
    def _append_log(self, text):
        self.log_area.append(text)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    # ==================================================
    def on_finished(self):
        self.status_label.setText("Proceso finalizado")
        self.progress.setValue(100)
        self.progress.setVisible(False)

        self.btn_process.setEnabled(True)
        self.btn_select.setEnabled(True)
        self.btn_select_output.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    # ==================================================
    # Cierre seguro
    # ==================================================
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Proceso en ejecución",
                "Hay un proceso en curso. ¿Deseas cancelarlo y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.standardButton.Yes:
                self.worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
