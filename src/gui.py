import sys
import subprocess

# ==================================================
# OCULTAR CONSOLAS DE SUBPROCESOS (Windows)
# ==================================================
if sys.platform == "win32":
    subprocess.CREATE_NO_WINDOW = 0x08000000


from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
