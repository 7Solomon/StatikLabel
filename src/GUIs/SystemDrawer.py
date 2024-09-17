
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint

class ObjectPainter(QWidget):
    def __init__(self, objects, connections, result=None):
        super().__init__()
        self.objects = objects
        self.connections = connections
        self.result = result
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
        if self.result:
            self.drawPolplan(qp)
        qp.end()

    def drawObjects(self, qp):
        colors = {
            'Loslager': QColor(255, 0, 0),
            'Festlager': QColor(0, 255, 0),
            'Biegesteifecke': QColor(0, 0, 255),
            'Normalkraftgelenk': QColor(255, 255, 0),
        }

        self.scale_factor = 100
        
        for obj_id, obj in self.objects.items():
            obj_type = obj['type']
            x, y = obj['coordinates']
            rotation = obj['rotation']

            # Scale and center the coordinates
            x = x * self.scale_factor + self.width() // 2
            y = -y * self.scale_factor + self.height() // 2

            # Draw the object (circle)
            qp.setPen(QPen(Qt.black))
            qp.setBrush(colors.get(obj_type, QColor(128, 128, 128)))
            qp.drawEllipse(x - 5, y - 5, 10, 10)
            qp.drawText(x + 10, y, obj_id)

            if rotation is not None:
                # Set up the pen for a dotted line
                pen = QPen(QColor(255, 0, 0), 5, Qt.DotLine)  # Dotted black line with width 2
                qp.setPen(pen)

                # Compute the end of the rotation line
                length = 100  # Length of the rotation line
                angle_radians = math.radians(rotation)
                delta_x = length * math.cos(angle_radians)
                delta_y = length * math.sin(angle_radians)  # Invert y for screen coordinates

                # Draw the rotation line
                qp.drawLine(x-delta_x, y-delta_y, x+delta_x, y+delta_y)


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

    def drawPolplan(self, qp):
        line_pen = QPen(Qt.blue, 2, Qt.DotLine)
        np_pen = QPen(Qt.red, 5)
        

        
        widget_width = self.width()
        widget_height = self.height()
        
        for scheibe in self.result['visualize'].values():
            qp.setPen(line_pen)
            # Scale and shift coordinates for the first point (HP1)
            x1 = scheibe['HP1'][0] * self.scale_factor + widget_width // 2
            y1 = -scheibe['HP1'][1] * self.scale_factor + widget_height // 2
            
            # Scale and shift coordinates for the second point (HP2)
            x2 = scheibe['HP2'][0] * self.scale_factor + widget_width // 2
            y2 = -scheibe['HP2'][1] * self.scale_factor + widget_height // 2
            
            # Calculate direction vector (dx, dy)
            dx = x2 - x1
            dy = y2 - y1
            
            # Normalize the direction vector to unit length
            length = (dx**2 + dy**2)**0.5
            dx /= length
            dy /= length
            
            # Extend the line to "infinity" (far beyond the widget dimensions)
            factor = max(widget_width, widget_height) * 2  # Extend it far beyond the visible screen
            x_start = x1 - dx * factor
            y_start = y1 - dy * factor
            x_end = x2 + dx * factor
            y_end = y2 + dy * factor
            
            # Draw the extended line
            qp.drawLine(x_start, y_start, x_end, y_end)
            
            # Draw the point NP and labels (no change needed here)
            x3 = scheibe['NP'][0] * self.scale_factor + widget_width // 2
            y3 = -scheibe['NP'][1] * self.scale_factor + widget_height // 2
            
            qp.setPen(np_pen)
            qp.drawPoint(x3, y3)
            
            # Labels for points
            qp.drawText(x1 + 30, y1, 'HP1')
            qp.drawText(x2 + 30, y2, 'HP2')
            qp.drawText(x3 + 30, y3, 'NP')


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

