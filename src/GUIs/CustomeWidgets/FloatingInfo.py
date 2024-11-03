from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics

class FloatingInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Customizable parameters
        self.max_width = 400
        self.padding = 20
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 50, 50, 200);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 18px;
            }
        """)
        
        self.layout.addWidget(self.info_label)
        
    def setMaxWidth(self, width):
        """Set maximum width for the widget"""
        self.max_width = width
        self.updateInfo(self.info_label.text())  # Refresh size
        
    def setPadding(self, padding):
        """Set padding for the widget"""
        self.padding = padding
        self.updateInfo(self.info_label.text())  # Refresh size
        
    def updateInfo(self, text):
        self.info_label.setText(text)
        
        # Calculate size based on content
        font_metrics = QFontMetrics(self.info_label.font())
        
        # Calculate width based on longest line
        max_line_width = max(font_metrics.horizontalAdvance(line) for line in text.split('\n'))
        # Calculate height based on number of lines
        text_height = font_metrics.lineSpacing() * len(text.split('\n'))
        
        # Apply size constraints
        new_width = min(max_line_width + self.padding * 2, self.max_width)
        new_height = text_height + self.padding * 2
        
        # Update sizes
        self.info_label.setFixedWidth(new_width - self.padding)
        self.setFixedSize(new_width, new_height)
        self.raise_()
        
    def sizeHint(self):
        return self.size()