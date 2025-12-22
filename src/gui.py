import sys

# Fase 2: Importar TODO
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Fase 3: Ahora sí, ocultar consolas
from utils.runtime import hide_subprocess_consoles
hide_subprocess_consoles()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()