import sys
import json
from PyQt5.QtWidgets import QApplication
from src.SystemDrawer import ObjectPainter
from src.normalize_system import *
from src.check_static import *

from src.Labler import ImageLabeler

def open_labeler():
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())

def open_system():
    objects,conenctions = get_normalization('./systems/03/label.json')
    app = QApplication(sys.argv)
    window = ObjectPainter(objects,conenctions)
    window.show()
    sys.exit(app.exec_())

def static():
    objects,conenctions = get_normalization('./systems/03/label.json')
    result = test(conenctions, objects)

    app = QApplication(sys.argv)
    window = ObjectPainter(objects, conenctions, result = result)
    window.show()
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    #open_labeler()
    #open_system()
    static()