import sys
import json
from PyQt5.QtWidgets import QApplication

from src.Labler import ImageLabeler

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())