from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


LAGER = [ "Festlager", "Loslager", "Festeeinspannung","Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk"]



### For ClickEdit

from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QCheckBox, 
    QDoubleSpinBox, 
    QLineEdit, 
    QDialogButtonBox, 
    QMessageBox,
    QComboBox,
    QSlider,
    QSpinBox
)


class HoverInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.layout = QVBoxLayout()
        self.info_label = QLabel()
        self.layout.addWidget(self.info_label)
        self.setLayout(self.layout)
        
    def update_info(self, node_info):
        self.info_label.setText(f"""
            Node ID: {node_info['id']}
            Coordinates: {node_info['coordinates']}
            Type: {node_info.get('type', 'Unknown')}
            """)
        self.adjustSize()


def show_edit_node_properties(node_info):
    """
    Open a dialog to edit node properties
    
    Args:
        node_info (dict): Dictionary of node properties to edit
    
    Returns:
        dict: Updated node properties, or None if canceled
    """
    # Create a dialog for editing
    dialog = QDialog()
    dialog.setWindowTitle("Edit Node Properties")
    layout = QVBoxLayout()
    
    # Dynamically create input fields for each property
    property_inputs = {}
    for key, value in node_info.items():
        # Label for the property
        label = QLabel(str(key))
        layout.addWidget(label)
        
        # Custom input based on key
        if key == 'type':
            # Dropdown for type
            input_widget = QComboBox()
            input_widget.addItems(LAGER)
            input_widget.setCurrentText(str(value))
            property_inputs[key] = input_widget
            layout.addWidget(input_widget)
        elif key == 'coordinates':
            # Custom coordinate input
            input_widget = QWidget()
            coord_layout = QHBoxLayout()
            
            x_spin = QSpinBox()
            x_spin.setRange(-50, 50)
            x_spin.setValue(value[0])
            
            y_spin = QSpinBox()
            y_spin.setRange(-50, 50)
            y_spin.setValue(value[1])
            
            coord_layout.addWidget(QLabel("X:"))
            coord_layout.addWidget(x_spin)
            coord_layout.addWidget(QLabel("Y:"))
            coord_layout.addWidget(y_spin)
            
            input_widget.setLayout(coord_layout)
            
            # Store both spin boxes for retrieval
            property_inputs[key] = (x_spin, y_spin)
            layout.addWidget(input_widget)
        elif key == 'rotation':
            # Rotation input with slider and spinbox
            input_widget = QWidget()
            rotation_layout = QHBoxLayout()
            checkbox = QCheckBox("Hinzufügen einer Wirkungslinie?")
            
            # Handle potential None value
            rotation_value = value if value is not None else 0
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 360)
            slider.setValue(int(rotation_value))
            slider.setEnabled(False)  # Disabled initially

            spin_box = QSpinBox()
            spin_box.setRange(0, 360)
            spin_box.setValue(int(rotation_value))
            spin_box.setEnabled(False)  # Disabled initially

            # Connect slider and spinbox
            slider.valueChanged.connect(spin_box.setValue)
            spin_box.valueChanged.connect(slider.setValue)
            
            # Enable/disable slider and spinbox based on checkbox state
            def update_rotation_inputs(state):
                enabled = state == Qt.Checked
                slider.setEnabled(enabled)
                spin_box.setEnabled(enabled)

            # Connect checkbox state to update function
            checkbox.stateChanged.connect(update_rotation_inputs)
            
            # Add widgets to the layout
            rotation_layout.addWidget(slider)
            rotation_layout.addWidget(spin_box)
            rotation_layout.addWidget(checkbox)
            
            input_widget.setLayout(rotation_layout)
            
            # Store rotation widgets
            property_inputs[key] = (slider, spin_box, checkbox)
            
            layout.addWidget(input_widget)
        else:
            # Default input for other properties
            input_widget = QLineEdit(str(value))
            property_inputs[key] = input_widget
            layout.addWidget(input_widget)

    # Add OK and Cancel buttons
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    dialog.setLayout(layout)
   
    # Execute the dialog
    if dialog.exec_() == QDialog.Accepted:
        # Update node_info with the values from input widgets
        for key, widget in property_inputs.items():
            try:
                if key == 'type':
                    node_info[key] = widget.currentText()
                elif key == 'coordinates':
                    node_info[key] = (widget[0].value(), widget[1].value())
                elif key == 'rotation':
                    slider, spin_box, checkbox = widget
                    node_info[key] = slider.value() if checkbox.isChecked() else None
                elif isinstance(widget, QLineEdit):
                    node_info[key] = widget.text()
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Could not process property {key}: {str(e)}")
                return None
        
        return node_info
    
    return None