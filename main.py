import sys
import json
from PyQt5.QtWidgets import QApplication
from src.test import *

from src.Labler import ImageLabeler

def open_labeler():
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    #open_labeler()
    test()