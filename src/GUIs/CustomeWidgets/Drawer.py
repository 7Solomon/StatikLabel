from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QToolBar, QListWidget, QLabel, QStackedWidget, QPushButton)
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainter, QPen, QColor

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QStackedWidget, QListWidget, QTreeView, QFileSystemModel,
                            QHeaderView)
from PyQt5.QtCore import Qt, QDir
import os

from src.GUIs.CustomeWidgets.FileManager import ExplorerWidget

class DrawerPanel(QWidget):
    def __init__(self, name, content=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if isinstance(content, QWidget):
            layout.addWidget(content)
        else:
            self.content = QListWidget()
            if content:
                self.content.addItems(content)
            layout.addWidget(self.content)
        
        self.setMinimumWidth(20)

class MultiPanelDrawer(QWidget):
    def __init__(self, panels = None, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create stacked widget to hold different panels
        self.stack = QStackedWidget()
        
        self.panels = panels or {'ansichten': DrawerPanel('ansichten'),}
        # Add panels to stack
        for panel in self.panels.values():
            self.stack.addWidget(panel)
        
        # Create button container for panel selection
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(0)
        
        # Create buttons for each panel
        self.buttons = {}
        for name in self.panels.keys():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setMaximumHeight(30)
            btn.clicked.connect(lambda checked, n=name: self.switch_panel(n))
            self.buttons[name] = btn
            self.button_layout.addWidget(btn)
        
        # Set initial active panel
        self.buttons["ansichten"].setChecked(True)
        
        # Add widgets to layout
        self.layout.addWidget(self.stack)
        self.layout.addWidget(self.button_container)
        
        # Set fixed width for the drawer
        self.setMinimumWidth(20*len(self.panels)+5)
        
        # Style the widget
        self.style_widgets()
    
    def switch_panel(self, panel_name):
        # Update button states
        for name, button in self.buttons.items():
            button.setChecked(name == panel_name)
        
        # Switch to selected panel
        self.stack.setCurrentWidget(self.panels[panel_name])
    
    def style_widgets(self):
        # Style the buttons
        button_style = """
            QPushButton {
                border: none;
                border-top: 1px solid #ccc;
                background: #f0f0f0;
                padding: 5px;
            }
            QPushButton:checked {
                background: #e0e0e0;
                border-top: 2px solid #0078d4;
            }
            QPushButton:hover {
                background: #e5e5e5;
            }
        """
        for button in self.buttons.values():
            button.setStyleSheet(button_style)