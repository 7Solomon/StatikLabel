import json
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QToolBar, QListWidget, QLabel, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from src.GUIs.ObjectManager import ObjectManagerWidget
from src.GUIs.SystemDrawer import ObjectPainter
from src.GUIs.CustomeWidgets.Ansichten import Ansichten
from src.GUIs.labelerWidget import ImageLabelWidget
from src.GUIs.CustomeWidgets.FileManager import ExplorerWidget
from src.GUIs.CustomeWidgets.Drawer import MultiPanelDrawer
from src.state import SharedData


class Interacter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Application")
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create and add toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.addWidget(QLabel("Task Bar"))
        toolbar.addSeparator()
        toolbar.setMovable(False)
        
        # Create the stacked widget
        self.stacked_display_area = QStackedWidget()
        self.shared_data = SharedData()
        # Create and add the display widgets
        self.display_area = ImageLabelWidget(self.shared_data)
        self.display_area.setStyleSheet("background-color: white;")
        self.display_area.setMinimumWidth(800)
        self.display_area.setMinimumHeight(600)
        
        # Create system widget (second page)
        self.system_widget = ObjectManagerWidget(self.shared_data)
        self.system_widget.setStyleSheet("background-color: lightgray;")
        
        # Add widgets to stacked widget
        self.stacked_display_area.addWidget(self.display_area)      # Index 0
        self.stacked_display_area.addWidget(self.system_widget)     # Index 1
        
        # Create Ansichten with proper elements
        self.ansichten = Ansichten(elements=[
            {'name': 'Labeler', 'function': lambda: self.stacked_display_area.setCurrentIndex(0)},
            {'name': 'System', 'function': lambda: self.stacked_display_area.setCurrentIndex(1)}
        ])
        
        self.explorer = ExplorerWidget(
            handle_image_selected=self.handle_image_selected,
            handle_json_selected=self.handle_json_selected,
            export_button_callback=self.handle_export_selected
        )
        self.explorer.setMinimumWidth(100)
        # Create the multi-panel drawer
        self.drawer = MultiPanelDrawer(panels={
            'ansichten': self.ansichten,
            'datein': self.explorer
        })
        
        # Add widgets to main layout
        main_layout.addWidget(self.stacked_display_area)
        main_layout.addWidget(self.drawer)
    
    def show_confimation(self):
        # Create a message box
        popup = QMessageBox()
        popup.setWindowTitle("?")
        popup.setText("Willst du wirklich fortfahren?")
        popup.setIcon(QMessageBox.Question)

        # Add Yes and No buttons
        popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        popup.setDefaultButton(QMessageBox.No)

        # Show popup and capture response
        response = popup.exec_()

        # Check response
        if response == QMessageBox.Yes:
            return True
        return False
    
    def handle_image_selected(self, img_path):
        """Handle image selection from ExplorerWidget"""
        try:
            # Load the image as QPixmap
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                raise Exception("Failed to load image")
                
            # Update the display area
            if self.show_confimation():
                self.display_area.load_image(pixmap)
                self.system_widget.object_painter.normalize_system()
            
            
        except Exception as e:
            # You might want to add proper error handling here
            print(f"Error loading image: {e}")
    
    def handle_json_selected(self, json_path):
        """Handle JSON selection from ExplorerWidget"""
        try:
            # Load the JSON data and update the display area
            with open(json_path, 'r') as f:
                data = json.load(f)
            if self.show_confimation():
                self.display_area.load_data(data)
                self.system_widget.object_painter.normalize_system()
            
        except Exception as e:
            # You might want to add proper error handling here
            print(e)
    def handle_export_selected(self, data):
        """Handle export button click from ExplorerWidget"""
        # Export the data to the selected path
        if self.show_confimation():
            data = self.display_area.get_data()
            self.explorer.export_to_selected_path(data)