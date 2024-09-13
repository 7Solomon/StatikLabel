
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint

class ObjectPainter(QWidget):
    def __init__(self, objects, connections):
        super().__init__()
        self.objects = objects
        self.connections = connections
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle('Normalized Objects and Connections Painter')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawObjects(qp)
        self.drawConnections(qp)
        qp.end()

    def drawObjects(self, qp):
        colors = {
            'Loslager': QColor(255, 0, 0),
            'Festlager': QColor(0, 255, 0),
            'Biegesteifecke': QColor(0, 0, 255),
            'Normalkrafrgelenk': QColor(255, 255, 0),
        }

        self.scale_factor = 100
        
        for obj_id, obj in self.objects.items():
            obj_type = obj['type']
            x, y = obj['coordinates']

            x = x * self.scale_factor + self.width() // 2
            y = -y * self.scale_factor + self.height() // 2

            qp.setBrush(colors.get(obj_type, QColor(128, 128, 128)))
            qp.drawEllipse(x - 5, y - 5, 10, 10)
            qp.drawText(x + 10, y, obj_id)

    def drawConnections(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)

        for (p1, p2), conn in self.connections.items():
            x1, y1 = self.objects[p1]['coordinates']
            x2, y2 = self.objects[p2]['coordinates']

            x1 = x1 * self.scale_factor + self.width() // 2
            y1 = -y1 * self.scale_factor + self.height() // 2
            x2 = x2 * self.scale_factor + self.width() // 2
            y2 = -y2 * self.scale_factor + self.height() // 2

            qp.drawLine(x1, y1, x2, y2)

            #if conn['orientation'] != 'diagonal':
            #    self.drawDimensionLine(qp, x1, y1, x2, y2, conn['normalized_length'])
            #else:
            #    self.drawDiagonalDimensions(qp, x1, y1, x2, y2, conn['normalized_length_x'], conn['normalized_length_y'])

    def drawDimensionLine(self, qp, x1, y1, x2, y2, length):
        offset = 20  # Offset for dimension line
        arrow_size = 10

        if x1 == x2:  # Vertical line
            dim_x1, dim_x2 = x1 + offset, x2 + offset
            dim_y1, dim_y2 = y1, y2
            text_x, text_y = dim_x1 + 5, (y1 + y2) // 2
        else:  # Horizontal line
            dim_x1, dim_x2 = x1, x2
            dim_y1, dim_y2 = y1 + offset, y2 + offset
            text_x, text_y = (x1 + x2) // 2, dim_y1 + 15

        # Draw dimension line
        qp.drawLine(dim_x1, dim_y1, dim_x2, dim_y2)

        # Draw arrows
        self.drawArrow(qp, QPoint(dim_x1, dim_y1), QPoint(dim_x2, dim_y2), arrow_size)
        self.drawArrow(qp, QPoint(dim_x2, dim_y2), QPoint(dim_x1, dim_y1), arrow_size)

        # Draw extension lines
        qp.drawLine(x1, y1, dim_x1, dim_y1)
        qp.drawLine(x2, y2, dim_x2, dim_y2)

        # Draw text
        qp.drawText(text_x, text_y, f"{length}L")

    def drawDiagonalDimensions(self, qp, x1, y1, x2, y2, length_x, length_y):
        offset = 20
        arrow_size = 10

        # X dimension
        dim_y = max(y1, y2) + offset
        qp.drawLine(x1, dim_y, x2, dim_y)
        qp.drawLine(x1, y1, x1, dim_y)
        qp.drawLine(x2, y2, x2, dim_y)
        self.drawArrow(qp, QPoint(x1, dim_y), QPoint(x2, dim_y), arrow_size)
        self.drawArrow(qp, QPoint(x2, dim_y), QPoint(x1, dim_y), arrow_size)
        qp.drawText((x1 + x2) // 2, dim_y + 15, f"{length_x}L")

        # Y dimension
        dim_x = max(x1, x2) + offset
        qp.drawLine(dim_x, y1, dim_x, y2)
        qp.drawLine(x1, y1, dim_x, y1)
        qp.drawLine(x2, y2, dim_x, y2)
        self.drawArrow(qp, QPoint(dim_x, y1), QPoint(dim_x, y2), arrow_size)
        self.drawArrow(qp, QPoint(dim_x, y2), QPoint(dim_x, y1), arrow_size)
        qp.drawText(dim_x + 5, (y1 + y2) // 2, f"{length_y}L")

    def drawArrow(self, qp, start, end, arrow_size):
        qp.save()
        qp.translate(end)

        # Calculate the angle using arctangent
        dx = start.x() - end.x()
        dy = start.y() - end.y()
        angle = math.degrees(math.atan2(dy, dx))

        qp.rotate(-angle)
        qp.drawLine(QPoint(0, 0), QPoint(-arrow_size, -arrow_size / 2))
        qp.drawLine(QPoint(0, 0), QPoint(-arrow_size, arrow_size / 2))
        qp.restore()

