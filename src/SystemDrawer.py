import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

class ObjectPainter(QWidget):
    def __init__(self, objects, connections):
        super().__init__()
        self.objects = objects
        self.connections = connections
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Normalized Objects and Connections Painter')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawObjects(qp)
        self.drawConnections(qp)
        qp.end()

    def drawObjects(self, qp):
        # Define different colors for different types
        colors = {
            'Loslager': QColor(255, 0, 0),  # Red
            'Festlager': QColor(0, 255, 0),  # Green
            'Biegesteifecke': QColor(0, 0, 255),  # Blue
            'Normalkrafrgelenk': QColor(255, 255, 0),  # Yellow
        }

        # Scaling factor to fit coordinates in the window
        self.scale_factor = 50
        
        for obj_id, obj in self.objects.items():
            obj_type = obj['type']
            x, y = obj['coordinates']

            # Translate coordinates (e.g., origin (0, 0) at the center)
            x = x * self.scale_factor + self.width() // 2
            y = -y * self.scale_factor + self.height() // 2  # Invert y for typical GUI coordinates

            # Set color based on object type
            qp.setBrush(colors.get(obj_type, QColor(128, 128, 128)))  # Default to gray if type not found

            # Draw a circle representing the object
            qp.drawEllipse(x - 5, y - 5, 10, 10)  # Draw circles with a 10px diameter

            # Draw the object ID next to the object
            qp.drawText(x + 10, y, obj_id)

    def drawConnections(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)  # Black lines for connections
        qp.setPen(pen)

        for (p1, p2), conn in self.connections.items():
            # Get coordinates of the connected objects
            x1, y1 = self.objects[p1]['coordinates']
            x2, y2 = self.objects[p2]['coordinates']

            # Translate coordinates to fit the canvas
            x1 = x1 * self.scale_factor + self.width() // 2
            y1 = -y1 * self.scale_factor + self.height() // 2  # Invert y for typical GUI coordinates
            x2 = x2 * self.scale_factor + self.width() // 2
            y2 = -y2 * self.scale_factor + self.height() // 2  # Invert y for typical GUI coordinates

            # Draw a line between the two objects
            qp.drawLine(x1, y1, x2, y2)

            # Display connection information (Angle and Length) near the midpoint of the line
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            qp.drawText(mid_x + 10, mid_y, f"Angle: {conn['angle']:.2f}, Length: {conn['length']}L")
