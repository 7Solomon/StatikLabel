import json
import mimetypes
from PyQt5.QtWidgets import (QWidget, QTreeView, QVBoxLayout, QFileSystemModel, 
                            QApplication, QStyle, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt, QDir
import sys
import os

class ExplorerWidget(QWidget):
    def __init__(self, root_path=None, handle_image_selected=None, handle_json_selected=None, export_button_callback=None):
        super().__init__()
        #self.root_path = root_path or os.path.expanduser("~")
        
        self.handle_image_selected = handle_image_selected
        self.handle_json_selected = handle_json_selected
        self.export_button_callback = export_button_callback
        
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
    
    def export_to_selected_path(self, data):
        src_path = self.get_selected_path()
        if src_path:
            file_name = os.path.join(src_path, 'label.json')
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print("No file selected")
