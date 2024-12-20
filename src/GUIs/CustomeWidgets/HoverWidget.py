from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


LAGER = [ "Festlager", "Loslager", "Festeeinspannung","Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk"]
CONNECTION_OPTIONS = ['fest', 'gelenkig']



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
    QSpinBox,
    QPushButton
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
            Rotation: {node_info.get('rotation', 'None')}
            Connections: {node_info.get('connections', 'None')}
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
        elif key == 'connections':
            connection_Widget = QWidget()
            connection_layout = QVBoxLayout(connection_Widget)
            
            # Store connection inputs for later access
            connection_inputs = []
            
            for i, conn in enumerate(value):
                hori_widget = QWidget()
                hori_layout = QHBoxLayout(hori_widget)

                # Destination input
                dest_input = QLineEdit(str(conn.get('to', '')))
                dest_input.setPlaceholderText("Enter node ID")
                hori_layout.addWidget(dest_input)

                # Connection type dropdown
                type_combo = QComboBox()
                type_combo.addItems(CONNECTION_OPTIONS)
                # Set the current type if it exists
                current_type = conn.get('type', CONNECTION_OPTIONS[0])
                type_index = type_combo.findText(current_type)
                if type_index >= 0:
                    type_combo.setCurrentIndex(type_index)
                hori_layout.addWidget(type_combo)

                # Remove button
                remove_button = QPushButton("Remove")
                remove_button.clicked.connect(lambda checked, w=hori_widget: remove_connection(w))
                hori_layout.addWidget(remove_button)

                connection_layout.addWidget(hori_widget)
                
                # Store inputs for later access
                connection_inputs.append((dest_input, type_combo))
            
            def add_new_connection():
                # Create a new connection widget
                new_hori_widget = QWidget()
                new_hori_layout = QHBoxLayout(new_hori_widget)

                # Destination input
                dest_input = QLineEdit()
                dest_input.setPlaceholderText("Enter node ID")
                new_hori_layout.addWidget(dest_input)

                # Connection type dropdown
                type_combo = QComboBox()
                type_combo.addItems(CONNECTION_OPTIONS)
                new_hori_layout.addWidget(type_combo)

                # Remove button
                remove_button = QPushButton("Remove")
                remove_button.clicked.connect(lambda checked, w=new_hori_widget: remove_connection(w))
                new_hori_layout.addWidget(remove_button)

                # Add the new connection to the layout
                connection_layout.insertWidget(connection_layout.count() - 1, new_hori_widget)
                
                # Add to connection inputs
                connection_inputs.append((dest_input, type_combo))

            def remove_connection(widget):
                # Find and remove the corresponding input from connection_inputs
                for input_pair in connection_inputs:
                    if input_pair[0].parent() == widget:
                        connection_inputs.remove(input_pair)
                        break
                
                # Remove the connection widget from layout
                connection_layout.removeWidget(widget)
                widget.deleteLater()

            add_button = QPushButton("Add Connection")
            add_button.clicked.connect(add_new_connection)
            connection_layout.addWidget(add_button)
            
            # Store connection inputs in property_inputs
            property_inputs['connections'] = connection_inputs
            
            layout.addWidget(connection_Widget)

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
                elif key == 'connections':
                    connections = []
                    for line_edit, combo_box in widget:
                        connections.append({
                            'to': line_edit.text(), 
                            'type': combo_box.currentText()
                        })
                    node_info[key] = connections
                elif isinstance(widget, QLineEdit):
                    node_info[key] = widget.text()
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Could not process property {key}: {str(e)}")
                return node_info
        
        return node_info
    
    return node_info

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
                             QSpinBox, QCheckBox, QDialogButtonBox, QWidget, 
                             QMessageBox, QPushButton)
from PyQt5.QtCore import Qt

def show_edit_node_properties_for_labeler(node_info):
    """
    Display a dialog for editing node properties with an improved layout and reset functionality.
    
    Args:
        node_info (dict): Dictionary containing node information
    
    Returns:
        dict: Updated node information
    """
    dialog = QDialog()
    dialog.setWindowTitle("Edit Node Properties")
    dialog.setMinimumWidth(400)  # Ensure a reasonable minimum width
    
    layout = QVBoxLayout()
    property_inputs = {}

    # Node ID Display (if available)
    node_id_layout = QHBoxLayout()
    node_id_label = QLabel("Node ID:")
    node_id_value = QLabel(str(node_info.get('id', 'N/A')))
    node_id_layout.addWidget(node_id_label)
    node_id_layout.addWidget(node_id_value)
    layout.addLayout(node_id_layout)

    # Rotation Section
    rotation_group = QWidget()
    rotation_layout = QVBoxLayout()
    
    # Checkbox and Reset Button Layout
    checkbox_reset_layout = QHBoxLayout()
    checkbox = QCheckBox("Add Rotation Line")
    reset_rotation_btn = QPushButton("Reset Rotation")
    reset_rotation_btn.setToolTip("Set rotation to None")
    
    # Handle potential None value
    value = node_info.get('rotation', None)
    rotation_value = value if value is not None else 0
    
    # Slider and Spinbox Layout
    slider_spinbox_layout = QHBoxLayout()
    slider = QSlider(Qt.Horizontal)
    slider.setRange(0, 360)
    slider.setValue(int(rotation_value))
    slider.setEnabled(False)

    spin_box = QSpinBox()
    spin_box.setRange(0, 360)
    spin_box.setValue(int(rotation_value))
    spin_box.setEnabled(False)

    # Connect slider and spinbox
    slider.valueChanged.connect(spin_box.setValue)
    spin_box.valueChanged.connect(slider.setValue)
    
    # Enable/disable slider and spinbox based on checkbox state
    def update_rotation_inputs(state):
        enabled = state == Qt.Checked
        slider.setEnabled(enabled)
        spin_box.setEnabled(enabled)
        reset_rotation_btn.setEnabled(enabled)

    # Reset rotation function
    def reset_rotation():
        slider.setValue(0)
        spin_box.setValue(0)
        checkbox.setChecked(False)

    # Connect signals
    checkbox.stateChanged.connect(update_rotation_inputs)
    reset_rotation_btn.clicked.connect(reset_rotation)
    
    # Add widgets to layouts
    checkbox_reset_layout.addWidget(checkbox)
    checkbox_reset_layout.addWidget(reset_rotation_btn)
    
    slider_spinbox_layout.addWidget(slider)
    slider_spinbox_layout.addWidget(spin_box)
    
    rotation_layout.addLayout(checkbox_reset_layout)
    rotation_layout.addLayout(slider_spinbox_layout)
    
    rotation_group.setLayout(rotation_layout)
    layout.addWidget(rotation_group)

    # Property tracking
    property_inputs['rotation'] = (slider, spin_box, checkbox)

    # Button Box
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
                if key == 'rotation':
                    slider, spin_box, checkbox = widget
                    node_info[key] = slider.value() if checkbox.isChecked() else None
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Could not process property {key}: {str(e)}")
                return node_info
    
    return node_info