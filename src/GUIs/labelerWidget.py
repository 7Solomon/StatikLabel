from typing import List

import math
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint, QSize, QRect

#from src.state import StateManager



class ImageWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.original_pixmap = None
        self.max_size = QSize(1920, 1080)
        
        #self.state_manager = StateManager()

        self.init_variables()

    def init_variables(self):

        self.connections = []
        self.objects = {}
        self.object_counter = 0
        
        self.connection_start = None

        self.rotation_object = None
        self.rotation_angle = 0
        self.is_rotating = False
        
    def setPixmap(self, pixmap):
        """Override setPixmap to store original and handle scaling"""
        if isinstance(pixmap, QPixmap):
            self.original_pixmap = pixmap
            scaled_pixmap = self.get_scaled_pixmap()
            super().setPixmap(scaled_pixmap)
            #self.draw_objects()  # Redraw objects when pixmap changes
    
    def load_data(self, data):
        """Load a previous state into the widget"""
        objects = data.get("objects", {})
        connections = data.get("connections", [])

        key_mapping = {}        
        object_counter = len(self.objects)
        if objects:
            if isinstance(next(iter(objects.values()))['coordinates'], list) and all(isinstance(x, int) for x in next(iter(objects.values()))['coordinates']):   # This just realizes the first elemnt works but could be better 
                if self.parent().askToNormalize():
                    for key, obj in objects.items():
                        new_key = chr(65 + object_counter)
                        scalar_x = obj['coordinates'][0] / self.original_pixmap.width()
                        scalar_y = obj['coordinates'][1] / self.original_pixmap.height()
                        self.objects[new_key] = {
                            "type": obj["type"],
                            "coordinates": (scalar_x, scalar_y),
                            "rotation": obj.get("rotation", None)
                        }
                        key_mapping[key] = new_key   # Um neue auf alt umzuwischen
                        object_counter += 1
                    new_connections = [[key_mapping[start], key_mapping[end]] for start, end in connections]
                    self.connections = new_connections
                                        
            elif isinstance(next(iter(objects.values()))['coordinates'], list) and all(isinstance(x, float) for x in next(iter(objects.values()))['coordinates']):
                self.objects = objects
                self.object_counter = object_counter
                self.connections = connections
        self.update()
    
    def get_scaled_pixmap(self):
        """Get properly scaled pixmap maintaining aspect ratio"""
        if not self.original_pixmap:
            return None
            
        return self.original_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw black background
        painter.fillRect(self.rect(), Qt.black)
        
        if self.original_pixmap:
            # Get the rectangle where the image should be drawn
            image_rect = self.get_image_rect()
            if image_rect:
                # Draw the base image
                painter.drawPixmap(image_rect, self.original_pixmap.scaled(
                    image_rect.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
 
                # Draw objects (nodes)
                painter.setPen(QPen(Qt.blue, 5))
                for identifier, obj in self.objects.items():
                    pos_x, pos_y = obj["coordinates"]
                    widget_point = self.image_to_widget_coords(pos_x, pos_y)
                    if widget_point:
                        painter.drawPoint(widget_point)
                        painter.drawText(widget_point + QPoint(5, 5), identifier)

                        # Draw rotation line of Object
                        if obj["rotation"] is not None:
                            rotation_line_length = 50
                            angle_rad = math.radians(obj["rotation"])                           
                            (end_x, end_y) = (widget_point.x() + rotation_line_length * math.cos(angle_rad), widget_point.y() + rotation_line_length * math.sin(angle_rad))
                            (start_x, start_y) = (widget_point.x() - rotation_line_length * math.cos(angle_rad), widget_point.y() - rotation_line_length * math.sin(angle_rad))
                            end_point = QPoint(int(end_x), int(end_y))
                            start_point = QPoint(int(start_x), int(start_y))

                            painter.setPen(QPen(Qt.red, 2, Qt.DotLine))  
                            painter.drawLine(start_point, end_point)
                        

                # Draw connections
                painter.setPen(QPen(Qt.green, 2))
                for start_id, end_id in self.connections:
                    start_x, start_y = self.objects[start_id]["coordinates"]
                    end_x, end_y = self.objects[end_id]["coordinates"]
                    
                    start_point = self.image_to_widget_coords(start_x, start_y)
                    end_point = self.image_to_widget_coords(end_x, end_y)
                    
                    if start_point and end_point:
                        painter.drawLine(start_point, end_point)
                

                # Rotation line
                if self.rotation_object:
                    obj_coords = self.objects[self.rotation_object]["coordinates"]
                    obj_point = self.image_to_widget_coords(*obj_coords)

                    # Calculate end point of the rotation line (extend to a reasonable length)
                    rotation_line_length = 100
                    angle_rad = math.radians(self.rotation_angle)
                    (end_x, end_y) = (widget_point.x() + rotation_line_length * math.cos(angle_rad), widget_point.y() + rotation_line_length * math.sin(angle_rad))
                    (start_x, start_y) = (widget_point.x() - rotation_line_length * math.cos(angle_rad), widget_point.y() - rotation_line_length * math.sin(angle_rad))
                    end_point = QPoint(int(end_x), int(end_y))
                    start_point = QPoint(int(start_x), int(start_y))

                    # Draw the rotation line
                    painter.setPen(QPen(Qt.red, 4, Qt.DotLine))
                    painter.drawLine(start_point, end_point)
                
                       
                

    def get_image_rect(self):
        """Get the actual rectangle where the image is displayed within the widget"""
        if not self.original_pixmap:
            return None
        
        # Get widget and pixmap dimensions
        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()
        
        # Calculate the scaling ratio while maintaining aspect ratio
        scale_w = widget_size.width() / pixmap_size.width()
        scale_h = widget_size.height() / pixmap_size.height()
        scale = min(scale_w, scale_h)
        
        # Calculate the actual dimensions of the displayed image
        image_width = int(pixmap_size.width() * scale)
        image_height = int(pixmap_size.height() * scale)
        
        # Calculate the position to center the image
        x = (widget_size.width() - image_width) // 2
        y = (widget_size.height() - image_height) // 2
        
        return QRect(x, y, image_width, image_height)

    def widget_to_image_coords(self, pos):
        """Convert widget coordinates to normalized image coordinates (0-1 range)"""
        if not self.original_pixmap:
            return None
            
        image_rect = self.get_image_rect()
        if not image_rect or not image_rect.contains(pos):
            return None
            
        # Convert to relative coordinates within the image (as floats)
        x_ratio = float((pos.x() - image_rect.x()) / image_rect.width())
        y_ratio = float((pos.y() - image_rect.y()) / image_rect.height())
        return (x_ratio, y_ratio)  # Return tuple of floats

    def image_to_widget_coords(self, x_ratio, y_ratio):
        """Convert normalized image coordinates (0-1 range) to widget coordinates"""
        if not self.original_pixmap:
            return None
            
        image_rect = self.get_image_rect()
        if not image_rect:
            return None
            
        # Convert from relative coordinates to widget coordinates
        x = image_rect.x() + (float(x_ratio) * image_rect.width())
        y = image_rect.y() + (float(y_ratio) * image_rect.height())
        return QPoint(int(x), int(y))

    def find_clicked_object(self, pos):
        """Find object near the clicked position"""
        if not self.original_pixmap:
            return None
            
        # Convert click position to image coordinates
        image_coords = self.widget_to_image_coords(pos)
        if not image_coords:
            return None
            
        click_x, click_y = image_coords
        
        # Search for nearby objects
        click_radius = 0.02  # 2% of image size as click radius
        for identifier, obj in self.objects.items():
            obj_x, obj_y = obj["coordinates"]
            distance = math.sqrt((click_x - obj_x)**2 + (click_y - obj_y)**2)
            if distance < click_radius:
                return identifier
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        if not self.original_pixmap:
            return
            
        parent = self.parent()
        if parent.connect_button.isChecked():
            self.add_connection(pos)
        elif parent.rotation_button.isChecked():
            self.handle_rotation_start(pos)
        else:
            object_type = parent.object_combo.currentText()
            self.place_object(pos, object_type)
        self.update()

    def place_object(self, pos, object_type):
        image_coords = self.widget_to_image_coords(pos)
        if not image_coords:
            return

        identifier = chr(65 + self.object_counter)
        self.objects[identifier] = {
            "type": object_type,
            "coordinates": image_coords,  # Store as tuple of floats
            "rotation": None
        }
        self.object_counter += 1
        self.update()

    ## Connect objects
    def add_connection(self, pos):
        self.handle_connection(pos)
        self.update()  
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

    ## Rotate objects
    def handle_rotation_start(self, pos):
        clicked_object = self.find_clicked_object(pos)
        if clicked_object:
            self.rotation_object = clicked_object
            self.is_rotating = True
    def mouseMoveEvent(self, event):
        if self.is_rotating and self.rotation_object:
            pos = event.pos()
            obj_coords = self.objects[self.rotation_object]["coordinates"]
            obj_point = self.image_to_widget_coords(*obj_coords)

            # Rotation angle in degrees
            dx = pos.x() - obj_point.x()
            dy = pos.y() - obj_point.y()
            self.rotation_angle = math.degrees(math.atan2(dy, dx))
            self.update()
    def mouseReleaseEvent(self, event):
        if self.is_rotating:
            # Save the rotation angle to the object
            self.objects[self.rotation_object]["rotation"] = self.rotation_angle
            self.is_rotating = False
            self.rotation_object = None
            self.update()
    

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        if self.original_pixmap:
            scaled_pixmap = self.get_scaled_pixmap()
            super().setPixmap(scaled_pixmap)


class ImageLabelWidget(QWidget):
    def __init__(self, provide_image_callback=None, parent=None):
        super().__init__(parent)
        self.provide_image_callback = provide_image_callback
        self.init_ui()
        
        
    def init_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create image display
        self.image_widget = ImageWidget()
        
        # Create controls with margins
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(10)
        
        self.object_combo = QComboBox()
        self.object_combo.addItems([
            "Loslager", "Festlager", "Einspannung", "Normalkrafteinspannung",
            "Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk", "Losesende"
        ])
        
        self.connect_button = QPushButton("Verbinde Objekte")
        self.connect_button.setCheckable(True)
        self.rotation_button = QPushButton("Definiere Wirkungslinie")
        self.rotation_button.setCheckable(True)
        
        controls_layout.addWidget(self.object_combo)
        controls_layout.addWidget(self.connect_button)
        controls_layout.addWidget(self.rotation_button)
        
        layout.addWidget(self.image_widget)
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        

    def load_image(self, pixmap):
        """Load image from provided QPixmap"""
        self.image_widget.init_variables()  ## Maybe danger
        self.image_widget.setPixmap(pixmap)

    def get_data(self):
        """Return the current state of the widget"""
        return {
            "objects": self.image_widget.objects,
            "connections": self.image_widget.connections
        }
        
    def load_data(self, data):
        """Load a previous state into the widget"""
        self.image_widget.load_data(data)
    def askToNormalize(self):
        popup = QMessageBox()
        popup.setWindowTitle("?")
        popup.setText("Deine daten sind in einem Absoluten wert, ich werde Sie laden und dann zu relativrn Konvertieren, dies kann zu Fehlern führen. Soll ich Trotzdem Fortfahren?")
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
        