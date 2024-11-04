from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QMainWindow, QSizePolicy, QStackedWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint, QSize

from src.GUIs.CustomeWidgets.FloatingInfo import FloatingInfoWidget
from src.GUIs.SystemDrawer import ObjectPainter

class ObjectManagerWidget(QWidget):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.main_layout = QVBoxLayout(self)
        
        # Create object painter
        self.object_painter = ObjectPainter(shared_data)
        self.object_painter.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        # Set minimum size to ensure the widget doesn't collapse
        self.object_painter.setMinimumSize(200, 200)  # Adjust these values as needed
        
        self.floating_info = FloatingInfoWidget(self)
        self.floating_info.move(10, 10)
        self.floating_info.show()

        self.main_layout.addWidget(self.object_painter)
        self.setup_controls()
        
    def setup_controls(self):
        # Create control panel widget and layout
        control_panel = QWidget()
        control_panel.setMaximumHeight(70)
        control_panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        control_layout = QHBoxLayout(control_panel)
        
        # Create object type selector
        self.object_type_selector = QComboBox()
        self.object_type_selector.addItems([
            'Loslager',
            'Festlager',
            'Gelenk',
            'Biegesteifecke',
            'Normalkraftgelenk'
        ])
        
        # Create placement button
        self.place_object_button = QPushButton('Objekt hinzufügen')
        self.place_object_button.setCheckable(True)
        self.place_object_button.clicked.connect(self.toggle_object_placement)
        
        # Add widgets to control layout
        control_layout.addWidget(self.object_type_selector)
        control_layout.addWidget(self.place_object_button)

        #connection_button = QPushButton('Connect')
        rotate_view_button = QPushButton('Rotate View')
        rotate_view_button.clicked.connect(lambda: self.object_painter.rotate_view(90))
        control_layout.addWidget(rotate_view_button)

        load_scheiben_button = QPushButton('Teile auf in scheiben')
        load_scheiben_button.clicked.connect(self.object_painter.load_scheiben)
        control_layout.addWidget(load_scheiben_button)
        load_pol_data_button = QPushButton('Lade den Polplan')
        load_pol_data_button.clicked.connect(self.object_painter.load_pol_data)
        control_layout.addWidget(load_pol_data_button)
        load_feste_scheiben_data_button = QPushButton('Lade die Festen scheiben')
        load_feste_scheiben_data_button.clicked.connect(self.object_painter.load_feste_scheiben)
        control_layout.addWidget(load_feste_scheiben_data_button)
        load_static_data_of_system_button = QPushButton('Lade Die Festherit des Systems')
        load_static_data_of_system_button.clicked.connect(self.object_painter.load_static_of_system)
        control_layout.addWidget(load_static_data_of_system_button)
        load_visualization_of_polplan_data_button = QPushButton('Lade die Visualisierung des Polplans')
        load_visualization_of_polplan_data_button.clicked.connect(self.object_painter.load_visualization_of_polplan_data)
        control_layout.addWidget(load_visualization_of_polplan_data_button)

        reload_button = QPushButton('Lade das System neu, und normalisiere es')
        reload_button.clicked.connect(self.object_painter.normalize_system)
        reload_button.clicked.connect(self.object_painter.init_variables)
        control_layout.addWidget(reload_button)
        
        
        #control_layout.addStretch()
        
        # Add control panel to main layout
        self.main_layout.addWidget(control_panel)
        self.main_layout.setStretchFactor(self.object_painter, 1)    ## Das kann wichtig sein, muss ausprobiert werden
    
    def toggle_object_placement(self):
        is_placing = self.place_object_button.isChecked()
        self.object_painter.set_placement_mode(
            is_placing,
            self.object_type_selector.currentText() if is_placing else None
        )
    
    