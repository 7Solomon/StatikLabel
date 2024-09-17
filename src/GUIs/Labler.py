import json
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint

class ImageLabeler(QMainWindow): 
    """"
    Hase Some weird scaling issues, but otherwise works fine
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Labeler")
        self.setGeometry(100, 100, 800, 600)
        self.labelObjects = ["Loslager", "Festlager", "Einspannung", "Normalkrafteinspannung", "Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk", "Losesende"]

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")

        self.object_combo = QComboBox()
        self.object_combo.addItems(self.labelObjects)

        self.load_button = QPushButton("Load Image")
        self.export_button = QPushButton("Export JSON")
        self.connect_button = QPushButton("Verbinde Objekte")
        self.connect_button.setCheckable(True)
        self.rotation_button = QPushButton("Definiere Wirkungslinie")
        self.rotation_button.setCheckable(True)
        self.load_labels_button = QPushButton("Load Labels")

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.object_combo)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.rotation_button)
        button_layout.addWidget(self.load_labels_button)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_button.clicked.connect(self.load_image)
        self.export_button.clicked.connect(self.export_json)
        self.load_labels_button.clicked.connect(self.load_json)
        self.image_label.mousePressEvent = self.on_image_click
        self.image_label.mouseMoveEvent = self.on_image_drag
        self.image_label.mouseReleaseEvent = self.on_image_release

        self.objects = {}
        self.connections = []
        self.rotation_lines = []
        self.object_counter = 0
        self.current_pixmap = None
        self.scaled_pixmap = None
        self.connection_start = None
        self.rotation_object = None
        self.rotation_line_end = None
        self.scale_factor = 1.0
        self.x_offset = 0
        self.y_offset = 0

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.current_pixmap = QPixmap(file_name)
            self.scale_factor = 1.0
            self.update_scaled_pixmap()

    def update_scaled_pixmap(self):
        if self.current_pixmap:
            label_size = self.image_label.size()
            scaled_size = self.current_pixmap.size().scaled(label_size, Qt.KeepAspectRatio)
            self.scale_factor = min(label_size.width() / self.current_pixmap.width(),
                                    label_size.height() / self.current_pixmap.height())
            self.scaled_pixmap = self.current_pixmap.scaled(
                scaled_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(self.scaled_pixmap)
            
            # Calculate and store offsets
            self.x_offset = (label_size.width() - scaled_size.width()) / 2
            self.y_offset = (label_size.height() - scaled_size.height()) / 2

    def on_image_click(self, event):
        if self.current_pixmap:
            pos = event.pos()
            scaled_pos = self.get_scaled_position(pos)

            if self.connect_button.isChecked():
                self.handle_connection(scaled_pos)
            elif self.rotation_button.isChecked():
                self.handle_rotation_start(scaled_pos)
            else:
                self.place_object(scaled_pos)

            self.draw_objects()

    def on_image_drag(self, event):
        if self.current_pixmap and self.rotation_object:
            pos = event.pos()
            scaled_pos = self.get_scaled_position(pos)
            self.rotation_line_end = scaled_pos
            self.draw_objects()

    def on_image_release(self, event):
        if self.rotation_object:
            pos = event.pos()
            scaled_pos = self.get_scaled_position(pos)
            self.handle_rotation_end(scaled_pos)
            self.rotation_object = None
            self.rotation_line_end = None
            self.draw_objects()

    def place_object(self, pos):
        object_type = self.object_combo.currentText()
        identifier = chr(65 + self.object_counter)
        self.objects[identifier] = {"type": object_type, "coordinates": (pos.x(), pos.y()), "rotation": None}
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
            self.connection_start = None

    def handle_rotation_start(self, pos):
        clicked_object = self.find_clicked_object(pos)
        if clicked_object:
            self.rotation_object = clicked_object

    def handle_rotation_end(self, pos):
        if self.rotation_object:
            start_pos = self.objects[self.rotation_object]["coordinates"]
            angle = self.calculate_angle(start_pos, (pos.x(), pos.y()))
            self.objects[self.rotation_object]["rotation"] = angle
            self.rotation_lines.append((self.rotation_object, angle))

    def calculate_angle(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return math.degrees(math.atan2(dy, dx))

    def find_clicked_object(self, pos):
        for identifier, obj in self.objects.items():
            obj_pos = QPoint(obj["coordinates"][0], obj["coordinates"][1])
            if (pos - obj_pos).manhattanLength() < 10:
                return identifier
        return None

    def get_scaled_position(self, pos):
        return QPoint(int((pos.x() - self.x_offset) / self.scale_factor),
                      int((pos.y() - self.y_offset) / self.scale_factor))

    def get_display_position(self, pos):
        return QPoint(int(pos.x() * self.scale_factor + self.x_offset),
                      int(pos.y() * self.scale_factor + self.y_offset))

    def draw_objects(self):
        if self.current_pixmap:
            pixmap = self.scaled_pixmap.copy()
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 5))

            # Draw objects (labels)
            for identifier, obj in self.objects.items():
                pos = self.get_display_position(QPoint(int(obj["coordinates"][0]), int(obj["coordinates"][1])))
                painter.drawPoint(pos)
                painter.drawText(pos + QPoint(5, 5), identifier)

            # Draw connections
            painter.setPen(QPen(Qt.blue, 2))
            for connection in self.connections:
                start = self.get_display_position(QPoint(int(self.objects[connection[0]]["coordinates"][0]), int(self.objects[connection[0]]["coordinates"][1])))
                end = self.get_display_position(QPoint(int(self.objects[connection[1]]["coordinates"][0]), int(self.objects[connection[1]]["coordinates"][1])))
                painter.drawLine(start, end)

            # Draw persistent rotation lines
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            for rotation_object, angle in self.rotation_lines:
                start = self.get_display_position(QPoint(int(self.objects[rotation_object]["coordinates"][0]), int(self.objects[rotation_object]["coordinates"][1])))
                self.draw_full_screen_line(painter, start, angle)

            # Draw temporary rotation line (full screen)
            if self.rotation_object and self.rotation_line_end:
                start = self.get_display_position(QPoint(int(self.objects[self.rotation_object]["coordinates"][0]), int(self.objects[self.rotation_object]["coordinates"][1])))
                angle = self.calculate_angle(self.objects[self.rotation_object]["coordinates"], (self.rotation_line_end.x(), self.rotation_line_end.y()))
                self.draw_full_screen_line(painter, start, angle)

            painter.end()
            self.image_label.setPixmap(pixmap)

    def draw_full_screen_line(self, painter, start, angle):
        width = self.image_label.width()
        height = self.image_label.height()

        rad = math.radians(angle)
        dx = math.cos(rad) * max(width, height)
        dy = math.sin(rad) * max(width, height)

        end1 = QPoint(start.x() - dx, start.y() - dy)
        end2 = QPoint(start.x() + dx, start.y() + dy)

        painter.drawLine(end1, end2)

    def export_json(self):
        data = {
            "objects": self.objects,
            "connections": self.connections,
            "rotation_lines": self.rotation_lines
        }
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)

    def load_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.objects = data.get("objects", {})
                self.connections = data.get("connections", [])
                self.rotation_lines = data.get("rotation_lines", [])
                self.object_counter = len(self.objects)
            self.draw_objects()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scaled_pixmap()
        self.draw_objects()

