import sys
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.GUIs.SystemDrawer import ObjectPainter
from src.GUIs.Interactiv import Interacter

from src.normalize_system import get_normalization_from_path, get_normalization
from src.statik.scheiben import get_scheiben
from src.statik.scan_pole import get_all_pole
from src.statik.check_statik import check_static_of_groud_scheiben, check_static_of_system
from src.statik.analyse import analyze_polplan



def open_system():
    objects,conenctions = get_normalization_from_path('./systems/03/label.json')
    app = QApplication(sys.argv)
    window = ObjectPainter(objects,conenctions)  # Adden von Nones vielleicht gut
    window.show()
    sys.exit(app.exec_())

def static():
    objects, conenctions = get_normalization_from_path('./systems/03/label.json')
    scheiben = get_scheiben(conenctions, objects)
    pol_data = get_all_pole(objects, scheiben['scheiben'], scheiben['scheiben_connection'])
    static_of_scheiben = check_static_of_groud_scheiben(pol_data['pole_of_scheiben'],objects)

    result = check_static_of_system(static_of_scheiben, pol_data['pole'], objects)
    weglinien,mismatches,is_valid = analyze_polplan(pol_data['pole'],objects)
    # Create visualization
    polplan_data = {
        'weglinien': weglinien,
        'mismatches': mismatches,
        'is_valid': is_valid
    }

    #print(pol_data)
    #print(static_of_scheiben)

    app = QApplication(sys.argv)
    window = ObjectPainter(objects, conenctions, scheiben, static_of_scheiben)
    
    window.show()
    sys.exit(app.exec_())

def test_interacter():
    
    app = QApplication(sys.argv)
    font = QFont("Arial", 8) 
    app.setFont(font)
    window = Interacter()
    
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    #open_labeler()
    #open_system()
    #static()
    test_interacter()