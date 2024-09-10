import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint


class ImageLabeler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Labeler")
        self.setGeometry(100, 100, 800, 600)
        self.labelObjects = ["Loslager", "Festlager", "Einspannung", "Normalkrafteinspannung", "Biegesteifecke", "Gelenk", "Normalkrafrgelenk", "Querkraftgelenk",]

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")

        self.object_combo = QComboBox()
        self.object_combo.addItems(self.labelObjects)

        self.load_button = QPushButton("Load Image")
        self.export_button = QPushButton("Export JSON")
        self.connect_button = QPushButton("Connect Mode")
        self.connect_button.setCheckable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.object_combo)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_button.clicked.connect(self.load_image)
        self.export_button.clicked.connect(self.export_json)
        self.image_label.mousePressEvent = self.on_image_click

        self.objects = {}
        self.connections = []
        self.object_counter = 0
        self.current_pixmap = None
        self.connection_start = None

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.current_pixmap = QPixmap(file_name)
            self.image_label.setPixmap(self.current_pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_image_click(self, event):
        if self.current_pixmap:
            pos = event.pos()
            scaled_pos = self.get_scaled_position(pos)

            if self.connect_button.isChecked():
                self.handle_connection(scaled_pos)
            else:
                self.place_object(scaled_pos)

            self.draw_objects()

    def place_object(self, pos):
        object_type = self.object_combo.currentText()
        identifier = chr(65 + self.object_counter)  # A, B, C, ...
        self.objects[identifier] = {"type": object_type, "coordinates": (pos.x(), pos.y())}
        self.object_counter += 1

    def handle_connection(self, pos):
        clicked_object = self.find_clicked_object(pos)
        if clicked_object:
            if self.connection_start is None:
                self.connection_start = clicked_object
            else:
                if self.connection_start != clicked_object:
                    self.connections.append((self.connection_start, clicked_object))
                self.connection_start = None
        else:
            # If no object was clicked, reset the connection start
            self.connection_start = None

    def find_clicked_object(self, pos):
        for identifier, obj in self.objects.items():
            obj_pos = QPoint(obj["coordinates"][0], obj["coordinates"][1])
            if (pos - obj_pos).manhattanLength() < 10:
                return identifier
        return None

    def get_scaled_position(self, pos):
        if self.current_pixmap:
            label_size = self.image_label.size()
            pixmap_size = self.current_pixmap.size()
            scaled_size = pixmap_size.scaled(label_size, Qt.KeepAspectRatio)
            x_offset = (label_size.width() - scaled_size.width()) / 2
            y_offset = (label_size.height() - scaled_size.height()) / 2
            x_scale = pixmap_size.width() / scaled_size.width()
            y_scale = pixmap_size.height() / scaled_size.height()
            return QPoint(int((pos.x() - x_offset) * x_scale), int((pos.y() - y_offset) * y_scale))
        return pos

    def draw_objects(self):
        if self.current_pixmap:
            pixmap = self.current_pixmap.copy()
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 5))
            
            for identifier, obj in self.objects.items():
                pos = QPoint(int(obj["coordinates"][0]), int(obj["coordinates"][1]))
                painter.drawPoint(pos)
                painter.drawText(pos + QPoint(5, 5), identifier)

            painter.setPen(QPen(Qt.blue, 2))
            for connection in self.connections:
                start = QPoint(int(self.objects[connection[0]]["coordinates"][0]), int(self.objects[connection[0]]["coordinates"][1]))
                end = QPoint(int(self.objects[connection[1]]["coordinates"][0]), int(self.objects[connection[1]]["coordinates"][1]))
                painter.drawLine(start, end)

            if self.connection_start:
                start = QPoint(int(self.objects[self.connection_start]["coordinates"][0]), int(self.objects[self.connection_start]["coordinates"][1]))
                end = self.get_scaled_position(self.image_label.mapFromGlobal(QCursor.pos()))
                
                # Only draw the preview line if the cursor is over a valid object
                if self.find_clicked_object(end):
                    painter.drawLine(start, end)

            painter.end()
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def export_json(self):
        data = {
            "objects": self.objects,
            "connections": self.connections
        }
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)