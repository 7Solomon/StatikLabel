from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QMainWindow, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint, QSize

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