import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


# Set your logo path. If the file is missing, a glass monogram is used.
LOGO_PATH = r"C:\Users\sdvseven\Documents\diplom\media\Untitled-1.png"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("")
    window = MainWindow(logo_path=LOGO_PATH)
    window.show()
    sys.exit(app.exec())
