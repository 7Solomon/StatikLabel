import json
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QToolBar, QListWidget, QLabel, QMessageBox, QStackedWidget, QPushButton, QToolButton, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from src.GUIs.ObjectManager import ObjectManagerWidget
from src.GUIs.SystemDrawer import ObjectPainter
from src.GUIs.CustomeWidgets.Ansichten import Ansichten
from src.GUIs.labelerWidget import ImageLabelWidget
from src.GUIs.CustomeWidgets.FileManager import ExplorerWidget
from src.GUIs.CustomeWidgets.Drawer import MultiPanelDrawer
from src.state import SharedData
from src.detection.test import get_new_data_format

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
        self.drawer_button = QToolButton()
        self.drawer_button.setText('Edit')
        self.drawer_button.clicked.connect(self.show_drawer_menu)  
        self.create_drawer_menu()  
        toolbar.addWidget(self.drawer_button)
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
            export_button_callback=self.handle_export_selected,
            export_to_new_format_button_callback=self.handle_export_to_new_format_selected,
        )
        self.explorer.setMinimumWidth(100)
        # Create the multi-panel drawer
        self.drawer = MultiPanelDrawer(panels={
            'ansichten': self.ansichten,
            'datein': self.explorer
        })

        # Add Show Button
        self.show_stuff_button = QPushButton("Grid")
        self.show_stuff_button.clicked.connect(self.system_widget.object_painter.drawGridBoolUpdate)
        toolbar.addWidget(self.show_stuff_button)
        self.stacked_display_area.currentChanged.connect(self.update_button_visibility)
        
        # Add widgets to main layout
        main_layout.addWidget(self.stacked_display_area)
        main_layout.addWidget(self.drawer)
    
    def update_button_visibility(self, index):
        """Show the button only when on the Drawer."""   ### Functioniert noch nicht? Ka wieso
        self.show_stuff_button.setVisible(index == 1)
    def create_drawer_menu(self):
        """Create the drawer menu"""
        self.drawer_menu = QMenu(self)

        action1 = QAction('Load', self)
        action1.triggered.connect(self.load_data_to_new_data_format)
        self.drawer_menu.addAction(action1)
    def show_drawer_menu(self):
        """ Show the drawer menu at the bottom-left corner of the button """
        # Show the drawer menu at the button's bottom-left corner
        self.drawer_menu.exec_(
            self.drawer_button.mapToGlobal(
                self.drawer_button.rect().bottomLeft()
            )
        )
    def load_data_to_new_data_format(self):
        data = self.shared_data.get_label_data()
        new_data = get_new_data_format(data, lambda a,b :self.show_auswahl(f'Verbindungstyp von ({a,b}) auswählen',['fest','gelenkig']))
        objects = new_data['objects']
        connections = new_data['connections']

    def show_auswahl(self, msg, options):
        popup = QMessageBox()
        popup.setWindowTitle("Auswahl")
        popup.setText(msg)
        popup.setIcon(QMessageBox.Question)

        # Add buttons
        buttons = {}
        for option in options:
            button = popup.addButton(option, QMessageBox.ActionRole)
            buttons[option] = button

        popup.exec_()

        clicked_button = popup.clickedButton()
        for label, button in buttons.items():
            if button == clicked_button:
                return label
        return None 



    def show_confimation(self,msg="Willst du wirklich fortfahren?"):
        # Create a message box
        popup = QMessageBox()
        popup.setWindowTitle("?")
        popup.setText(msg)
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
    def handle_export_selected(self):
        """Handle export button click from ExplorerWidget"""
        # Export the data to the selected path
        if self.show_confimation():
            data = self.display_area.get_data()
            self.explorer.export_to_selected_path(data)
    def handle_export_to_new_format_selected(self, data):
         if self.show_confimation():
            data = self.display_area.get_data()
            print('data',data)
            #self.explorer.export_to_selected_path(data)
