from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFileDialog
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Herramienta Scanner – Bodega")
        self.resize(800, 500)

        # ---- Widgets ----
        title = QLabel("Herramienta de Scanner de Facturas")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.btn_select = QPushButton("Seleccionar PDF")
        self.btn_process = QPushButton("Procesar")
        self.btn_process.setEnabled(False)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        # ---- Layouts ----
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_select)
        buttons_layout.addWidget(self.btn_process)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.log_area)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.btn_select.clicked.connect(self.select_pdf)
        self.selected_pdf = None


    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        if file_path:
            self.log_area.append(f"PDF seleccionado: {file_path}")
            self.btn_process.setEnabled(True)
