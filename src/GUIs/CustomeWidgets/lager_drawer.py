from PyQt5.QtWidgets import  QGraphicsItem
from PyQt5.QtGui import QBrush, QPen, QColor, QPolygon
from PyQt5.QtCore import QRectF, Qt, QPointF, QPoint

line_length = 30
line_spacing = 5
size = 20 

def drawSchraffur(qp, start_x, start_y, end_x, end_y):

    qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
    for j in range(6):  # 5 Schraffurlinien
        offset = j * int(30//6)  # Abstand zwischen den Linien
        qp.drawLine(
            start_x + offset, 
            start_y + line_spacing, 
            end_x + offset - 10, 
            end_y + 10
        )

def translateAndRotate(qp, x, y, rotation):
    # Translate and rotate for the Festlager
    qp.translate(x, y)                        
    if rotation:
        qp.rotate(rotation + 180)##########!!! VERY SCUFFED
    else:
        qp.rotate(180)##########!!! VERY SCUFFED
def drawLoslager(qp, x, y, rotation):
    qp.save()
    # Translate and rotate for the Loslager
    translateAndRotate(qp, x, y, rotation)

    # Draw Loslager (triangle and circle)
    qp.setPen(QPen(Qt.black, 2))
    qp.setBrush(QBrush(QColor(120, 0, 0)))
    # Draw the triangle
    points = [
        QPointF(-size / 2, size / 2),
        QPointF(size / 2, size / 2),
        QPointF(0, -size / 2),
    ]
    qp.drawPolygon(*points)

    # Draw a small circle at the bottom
    qp.setBrush(QColor(0, 0, 0))
    qp.drawEllipse(QPointF(0, size / 2 + 5), 5, 5)

    qp.drawLine(-line_length / 2, size / 2 + line_spacing, line_length / 2, size / 2 + line_spacing)

    # Restore the painter state
    qp.restore()


def drawFestlager(qp, x, y, rotation):
    # Save the current painter state
    qp.save()

    translateAndRotate(qp, x, y, rotation)

    # Set up the painter
    qp.setPen(QPen(Qt.black, 2))
    qp.setBrush(QBrush(QColor(0, 255, 0)))  # Green color for the triangle

    # Draw the triangle
    size = 20  # Size of the triangle
    triangle_points = [
        QPointF(-size / 2, size / 2),
        QPointF(size / 2, size / 2),
        QPointF(0, -size / 2),
    ]
    qp.drawPolygon(*triangle_points)

    # Draw two parallel lines below the triangle
    qp.setPen(QPen(Qt.black, 2))  # Black color for the lines
    start_point_x, start_point_y = (-line_length / 2, size / 2 + line_spacing)
    end_point_x, end_point_y = (line_length / 2, size / 2 + line_spacing)
    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
    #qp.drawLine(-line_length / 2, size / 2 + line_spacing, line_length / 2, size / 2 + line_spacing)
    drawSchraffur(qp, start_point_x, start_point_y, end_point_x, end_point_y)
    #qp.drawLine(-line_length / 2, size / 2 + 2 * line_spacing, line_length / 2, size / 2 + 2 * line_spacing)

    # Restore the painter state
    qp.restore()

def drawFesteEinspannung(qp, x, y, rotation):
    qp.save()

    # Translate and rotate for the Festlager
    translateAndRotate(qp, x, y, rotation)

    qp.setPen(QPen(Qt.black, 2))  # Black color for the lines
    start_point_x, start_point_y = (-line_length / 2, size / 2 + line_spacing)
    end_point_x, end_point_y = (line_length / 2, size / 2 + line_spacing)
    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
    drawSchraffur(qp, start_point_x, start_point_y, end_point_x, end_point_y)
    qp.restore()

def drawNormalkraftEinspannung(qp, x, y, rotation):
    qp.save()

    translateAndRotate(qp, x, y, rotation)
    
    qp.setPen(QPen(Qt.black, 2))  # Black color for the lines
    start_point_x, start_point_y = (-line_length / 2, size / 2)
    end_point_x, end_point_y = ( line_length / 2, size / 2)
    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
    #qp.drawLine(-line_length / 2, size / 2 + line_spacing, line_length / 2, size / 2 + line_spacing)
    drawSchraffur(qp, start_point_x, start_point_y, end_point_x, end_point_y)
    qp.restore()

#def drawQuerkraftEinspannung(qp, x, y, rotation):
def drawQNGelenk(qp, x, y, rotation):
    qp.save()

    translateAndRotate(qp, x, y, rotation)
    
    qp.setPen(QPen(Qt.black, 2))  # Black color for the lines
    start_point_x, start_point_y = (-line_length / 2, size / 2)
    end_point_x, end_point_y = (line_length / 2, size / 2)
    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
    
    start_point_x, start_point_y = (-line_length / 2, - size / 2)
    end_point_x, end_point_y = (line_length / 2,- size / 2)
    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)

    qp.restore()
#def drawNormalkraftGelenk(qp, x, y, rotation):
#    qp.save()
#
#    translateAndRotate(qp, x, y, rotation)
#    
#    qp.setPen(QPen(Qt.black, 2))  # Black color for the lines
#    start_point_x, start_point_y = (-line_length / 2, size / 2)
#    end_point_x, end_point_y = (line_length / 2, size / 2)
#    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
#    
#    start_point_x, start_point_y = (-line_length / 2, - size / 2)
#    end_point_x, end_point_y = (line_length / 2,- size / 2)
#    qp.drawLine(start_point_x, start_point_y, end_point_x, end_point_y)
#
#    qp.restore()

def drawBiegesteifecke(qp, x, y, rotation):
    qp.save()

    translateAndRotate(qp, x, y, rotation)
    
    qp.setBrush(Qt.black)  # Set the brush color to black
    qp.setPen(Qt.black)   # Set the outline color to black

    # Points
    triangle_points = [
        QPointF(-size / 8, size / 8),
        QPointF(size / 8, size / 8),
        QPointF(0, -size / 8),
    ]
    qp.drawPolygon(*triangle_points)
    qp.restore()


def drawGelenk(qp, x, y, rotation):
    qp.save()
    qp.setPen(QPen(Qt.black, 2))
    radius = 5  # Half the size of the ellipse (width/2 and height/2)
    qp.drawEllipse(x - radius, y - radius, 2 * radius, 2 * radius)
    qp.restore()

