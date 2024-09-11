import sys
import json
from PyQt5.QtWidgets import QApplication
from src.SystemDrawer import ObjectPainter
from src.test import *

from src.Labler import ImageLabeler

def open_labeler():
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())

def open_system():
    objects,conenctions = test()
    app = QApplication(sys.argv)
    window = ObjectPainter(objects,conenctions)
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    #open_labeler()
    open_system()