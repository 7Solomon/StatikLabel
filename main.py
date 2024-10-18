import sys
import json
from PyQt5.QtWidgets import QApplication
from src.GUIs.SystemDrawer import ObjectPainter
from src.GUIs.Labler import ImageLabeler

from src.normalize_system import get_normalization
from src.statik.scheiben import get_scheiben
from src.statik.scan_pole import get_all_pole
from src.statik.check_statik import check_static_of_groud_scheiben


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
    objects, conenctions = get_normalization('./systems/03/label.json')
    scheiben = get_scheiben(conenctions, objects)
    pol_data = get_all_pole(objects, scheiben['scheiben'], scheiben['scheiben_connection'])
    check_static_of_groud_scheiben(pol_data['pole_of_scheiben'],objects)

    app = QApplication(sys.argv)
    window = ObjectPainter(objects, conenctions)
    window.show()
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    #open_labeler()
    #open_system()
    static()