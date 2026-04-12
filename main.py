import sys
import os

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    # Load global stylesheet
    qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles", "main.qss")
    with open(qss_path, "r", encoding="utf-8") as fh:
        app.setStyleSheet(fh.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
