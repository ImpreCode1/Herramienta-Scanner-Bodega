from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFileDialog, QProgressBar
    QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFileDialog, QProgressBar
)
from ui.worker import ScannerWorker
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from pathlib import Path
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Herramienta Scanner – Bodega")
        self.resize(800, 500)

        # ---- Widgets ----
        title = QLabel("Scanner de Facturas")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        logo = QLabel()
        pixmap = QPixmap(str(resource_path("src/assets/logo_impresistem.png")))
        logo.setPixmap(pixmap.scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

        subtitle = QLabel("Separación automática por códigos de barras")
        subtitle.setStyleSheet("color: #475569; margin-bottom: 10px;")
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        header_layout.addWidget(logo)

        text_layout = QVBoxLayout()
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        self.btn_select = QPushButton("Seleccionar PDF")
        self.btn_select_output = QPushButton("Seleccionar carpeta de salida")
        self.btn_select_output = QPushButton("Seleccionar carpeta de salida")
        self.btn_process = QPushButton("Procesar")
        self.btn_process.setEnabled(False)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        

        # ---- Layouts ----
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_select)
        buttons_layout.addWidget(self.btn_select_output)
        buttons_layout.addWidget(self.btn_select_output)
        buttons_layout.addWidget(self.btn_process)
        
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

        self.btn_select.setStyleSheet("padding: 6px 12px;")
        self.btn_select_output.setStyleSheet("padding: 6px 12px;")
        
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
        
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5f5;
                border-radius: 6px;
                text-align: center;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 6px;
            }
        """)

        main_layout = QVBoxLayout()

        main_layout.addLayout(header_layout)   # 👈 PRIMERO
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.log_area)
        main_layout.addWidget(self.progress)

        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        buttons_layout.setSpacing(10)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.btn_select.clicked.connect(self.select_pdf)
        self.selected_pdf = None
        self.btn_process.clicked.connect(self.process_pdf)
        self.output_dir = None
        
        self.btn_select_output.clicked.connect(self.select_output_dir)
        
        
        self.output_dir = None
        
        self.btn_select_output.clicked.connect(self.select_output_dir)
        
        



    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        if file_path:
            self.selected_pdf = file_path
            self.log_area.append(f"PDF seleccionado: {file_path}")

            if self.output_dir:
                self.btn_process.setEnabled(True)


            if self.output_dir:
                self.btn_process.setEnabled(True)

            
    def process_pdf(self):
        if not self.selected_pdf or not self.output_dir:
        if not self.selected_pdf or not self.output_dir:
            return

        # UI se prepara
        # UI se prepara
        self.btn_process.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Crear worker
        self.worker = ScannerWorker(self.selected_pdf, self.output_dir)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Crear worker
        self.worker = ScannerWorker(self.selected_pdf, self.output_dir)

        # 🔗 CONEXIONES (AQUÍ VA LA LÍNEA)
        # 🔗 CONEXIONES (AQUÍ VA LA LÍNEA)
        self.worker.log.connect(self.log_area.append)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)

        # Arrancar
        # Arrancar
        self.worker.start()


    def on_finished(self):
        self.log_area.append("Proceso terminado.")
        self.btn_process.setEnabled(True)
        self.progress.setValue(100)
        self.progress.setVisible(False)

    
    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de salida"
        )

        if directory:
            self.output_dir = directory
            self.log_area.append(f"Carpeta de salida: {directory}")

            if self.selected_pdf:
                self.btn_process.setEnabled(True)
                

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(relative_path)
