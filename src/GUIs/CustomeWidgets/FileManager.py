import json
import mimetypes
from PyQt5.QtWidgets import (QWidget, QTreeView, QVBoxLayout, QFileSystemModel, 
                            QApplication, QStyle, QHeaderView, QPushButton, QDialog, QDialogButtonBox, QLabel, QHBoxLayout, QLineEdit)
from PyQt5.QtCore import Qt, QDir
import sys
import os

class ExplorerWidget(QWidget):
    def __init__(self, root_path=None, handle_image_selected=None, handle_json_selected=None, export_button_callback=None,export_to_new_format_button_callback=None):
        super().__init__()
        #self.root_path = root_path or os.path.expanduser("~")
        
        self.handle_image_selected = handle_image_selected
        self.handle_json_selected = handle_json_selected
        self.export_button_callback = export_button_callback
        self.export_to_new_format_button_callback = export_to_new_format_button_callback
        
        self.root_path = "./systems"
        self.init_ui()
        
    def init_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create file system model
        self.model = QFileSystemModel()
        
        # Important: Set root path before setting the model on the tree
        root_index = self.model.setRootPath(self.root_path)
        
        # Set filters to show all files and directories
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        
        # Create tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        
        # Critical: Set the root index AFTER setting the model
        self.tree.setRootIndex(root_index)  # Use the index returned by setRootPath
        
        # Set up the view
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.AscendingOrder)
        self.tree.setWindowTitle("Datein")
        
        # Hide unnecessary columns and set the name column to stretch
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)
        
        # Add tree to layout
        layout.addWidget(self.tree)

        # Add export button
        self.export_button = QPushButton("Export Selected File")
        layout.addWidget(self.export_button)
        self.export_button.clicked.connect(self.export_button_callback)
        self.new_format_export_button = QPushButton("New Format")
        layout.addWidget(self.new_format_export_button)
        self.new_format_export_button.clicked.connect(self.export_to_new_format_button_callback)
        
        # Set some reasonable default size
        self.setMinimumSize(300, 400)
        
        # Connect double-click signal
        self.tree.doubleClicked.connect(self.on_double_click)
        
    def on_double_click(self, index):
        # Get the file path
        path = self.model.filePath(index)
        file_type, encoding = mimetypes.guess_type(path)
        if file_type in ['image/png', 'image/jpeg']:
            if self.handle_image_selected:
                self.handle_image_selected(path)
            #print('Opening image:', path)
        elif file_type == 'application/json': 
            if self.handle_json_selected:
                self.handle_json_selected(path)
            #print('Opening JSON:', path)
    def get_selected_path(self):
        indexes = self.tree.selectedIndexes()
        if indexes:
            return self.model.filePath(indexes[0])
        return None
    def display_current_header(self, header_data):
        dialog = QDialog()
        dialog.setWindowTitle("Edit Header")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        line_edits = {}
        if header_data:
            for key, value in header_data.items():
                h_widget = QWidget()
                h_layout = QHBoxLayout(h_widget)
                h_layout.addWidget(QLabel(f"{key}"))
                line_edit = QLineEdit()
                line_edit.setText(str(value))
                h_layout.addWidget(line_edit)
                
                line_edits[key] = line_edit
                layout.addWidget(h_widget)
        else:
            layout.addWidget(QLabel("Keine header data gefunden, aber wird trotzdem erstellt"))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            updated_header_data = {}
            for key, line_edit in line_edits.items():
                updated_header_data[key] = line_edit.text()
            print("Updated Header Data:", updated_header_data)
            return updated_header_data
        
        return None
    
    def export_to_selected_path(self, data):
        src_path = self.get_selected_path()
        if src_path:
            if src_path.endswith('label.json'):
                file_name = src_path
            else:
                file_name = os.path.join(src_path, 'label.json')
        if file_name:
            header_data = self.display_current_header(data.get('header', None))
            to_save = {'header':header_data, **data}
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print("No file selected")
