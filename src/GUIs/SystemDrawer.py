
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QTransform
from PyQt5.QtCore import Qt, QPoint, QSize, QPointF

from src.normalize_system import get_normalization

class ObjectPainter(QWidget):
    def __init__(self, shared_data, scheiben= None, static_information= None, result=None):
        super().__init__()
        self.shared_data = shared_data
        self.shared_data.add_observer(self.init_variables)

        self.is_placing_object = False
        self.selected_object_type = None
        self.snap_threshold = 0.333  # How close to gridline to snap (in grid units)
        self.rotation_angle = 0

        self.normalize_system()
        self.init_variables()
        
    def normalize_system(self):
        data = self.shared_data.get_label_data()
        #print(f'Normaliize: {data}')
        if not len(data.get('objects',[])) == 0 and not len(data.get('connections',[])) == 0:
            objects, connections = get_normalization(data)
            self.shared_data.update_data('normalized_connections', connections)
            self.shared_data.update_data('normalized_objects', objects)
            #self.get_feste_scheiben_nodes()    
        #self.init_variables()

    def init_variables(self):
        self.view_range = 10
        self.scale_factor = 100
        self.offset = QPoint(0, 0) 
        self.last_mouse_pos = None

        data = self.shared_data.get_normalized_system()
        self.objects, self.connections = data.get('normalized_objects',{}), data.get('normalized_connections',[])
        self.result = None                      #
        self.scheiben = None                    #  Hier das sollte richtig gadded werden      
        self.static_information = None          #
        self.feste_nodes = []

        #if not len(data.get('objects',[])) == 0 and not len(data.get('connections',[])) == 0:
        #    self.objects, self.connections = get_normalization(data)
        #    self.get_feste_scheiben_nodes()
        self.update()
    
    def initUI(self):
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle('Normalized Objects and Connections Painter')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        ## Für drag und Rotation
        # Enable antialiasing ka was das ist
        qp.setRenderHint(QPainter.Antialiasing)
        qp.translate(self.offset)
        if self.rotation_angle != 0:
            qp.translate(self.width() // 2, self.height() // 2)
            qp.rotate(self.rotation_angle)
            qp.translate(-self.width() // 2, -self.height() // 2)


        self.drawGrid(qp)
        self.drawObjects(qp)
        self.drawConnections(qp)

        self.drawPreview(qp)

        if self.result:
            self.drawPolplan(qp)
        qp.end()
    def drawGrid(self, qp):
        grid_pen = QPen(QColor(200, 200, 200))
        grid_pen.setStyle(Qt.DashLine)
        qp.setPen(grid_pen)
        
        # Grid spacing and range
        grid_spacing = self.scale_factor
        center_x = self.width() // 2
        center_y = self.height() // 2

        # Calculate grid boundaries that exceed widget dimensions for full grid coverage
        start_x = center_x - self.view_range * grid_spacing
        end_x = center_x + self.view_range * grid_spacing
        start_y = center_y - self.view_range * grid_spacing
        end_y = center_y + self.view_range * grid_spacing

        # Draw vertical grid lines that extend beyond the window boundaries
        for i in range(-self.view_range, self.view_range + 1):
            x = center_x + i * grid_spacing
            qp.drawLine(x, start_y, x, end_y)  # Extend from start_y to end_y

        # Draw horizontal grid lines that extend beyond the window boundaries
        for i in range(-self.view_range, self.view_range + 1):
            y = center_y + i * grid_spacing
            qp.drawLine(start_x, y, end_x, y)  # Extend from start_x to end_x

        # Draw coordinate axes
        qp.setPen(QPen(Qt.black, 2))
        # X-axis
        qp.drawLine(start_x, center_y, end_x, center_y)
        # Y-axis
        qp.drawLine(center_x, start_y, center_x, end_y)

        # Draw axis labels
        qp.drawText(end_x - 20, center_y - 10, "x")
        qp.drawText(center_x + 10, start_y + 20, "y")

        # Draw grid numbers along axes
        for i in range(-self.view_range, self.view_range + 1):
            # X-axis numbers
            x = center_x + i * grid_spacing
            if i != 0:
                qp.drawText(x - 10, center_y + 20, str(i))
                
            # Y-axis numbers
            y = center_y - i * grid_spacing
            if i != 0:
                qp.drawText(center_x + 10, y + 5, str(i))

    def get_feste_scheiben_nodes(self):
        if self.static_information:
            for key,e in self.static_information.items():
                if e['static'] == True:
                    self.feste_nodes.extend(self.scheiben['scheiben'][key]['nodes'])
                    

    def drawObjects(self, qp):
        colors = {
            'Loslager': QColor(120, 0, 0),
            'Festlager': QColor(0, 255, 0),
            'Biegesteifecke': QColor(0, 0, 255),
            'Normalkraftgelenk': QColor(255, 255, 0),
        }

        if self.objects:
            for obj_id, obj in self.objects.items():
                obj_type = obj['type']
                x, y = obj['coordinates']
                rotation = obj['rotation']

                # Scale and center the coordinates
                x = x * self.scale_factor + self.width() // 2
                y = -y * self.scale_factor + self.height() // 2


                if obj_id in self.feste_nodes:
                    qp.setPen(QPen(Qt.black))
                    qp.setBrush(QColor(255, 0, 0))
                    qp.drawEllipse(x - 5, y - 5, 10, 10)
                    qp.drawText(x + 10, y, obj_id)
                
                else:
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
        if self.connections:
            for (p1, p2), conn in self.connections.items():
                
                # Check if Conenction is scheiben conenction
                if p1 in self.feste_nodes and p2 in self.feste_nodes:
                    qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Red lines for connections in 'scheiben'
                else:
                    qp.setPen(QPen(Qt.black, 2, Qt.SolidLine))  # Black for other connections


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
    
    # For Drag stuff
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.last_mouse_pos = event.pos()
        elif event.button() == Qt.LeftButton:
            if self.is_placing_object:
                self.set_new_node(event.pos()) 
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_placing_object:
            # Just update to show potential placement position
            self.update()
            
        elif self.last_mouse_pos is not None:

            # Calculate how much the mouse has moved
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta  # Update the offset with the delta
            self.last_mouse_pos = event.pos()  # Update the last mouse position
            self.update()  # Trigger a repaint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None  # Reset the last mouse position on release

    ### For add object stuff
    def set_placement_mode(self, is_placing, object_type=None):
        """Enable or disable object placement mode"""
        self.is_placing_object = is_placing
        self.selected_object_type = object_type
        self.setCursor(Qt.CrossCursor if is_placing else Qt.ArrowCursor)
        self.update()

    def snap_to_grid(self, pos):
        # Convert screen coordinates to grid coordinates
        grid_x = (pos.x() - self.width() // 2 - self.offset.x()) / self.scale_factor
        grid_y = -(pos.y() - self.height() // 2 - self.offset.y()) / self.scale_factor
        
        # Function to snap individual coordinate
        def snap_coordinate(coord):
            # Get the nearest whole, half, and third points
            whole = round(coord)
            half = round(coord * 2) / 2
            third = round(coord * 3) / 3
            
            # Find distances to each snap point
            dist_whole = abs(coord - whole)
            dist_half = abs(coord - half)
            dist_third = abs(coord - third)
            
            # Find the closest snap point within threshold
            if min(dist_whole, dist_half, dist_third) <= self.snap_threshold:
                if dist_whole <= dist_half and dist_whole <= dist_third:
                    return whole
                elif dist_half <= dist_third:
                    return half
                else:
                    return third
            return coord
        
        # Snap both coordinates
        snapped_x = snap_coordinate(grid_x)
        snapped_y = snap_coordinate(grid_y)
        
        return snapped_x, snapped_y
    def set_new_node(self, pos):
        """Add a new node at the given position with letter-based ID"""
        # Get snapped coordinates
        snapped_x, snapped_y = self.snap_to_grid(pos)

        new_id = chr(65 + len(self.objects))  # 65 is ASCII for 'A'
        # Create new object
        new_object = {
            'type': self.selected_object_type,
            'coordinates': [snapped_x, snapped_y],
            'rotation': None
        }
        self.objects[new_id] = new_object

        # Update shared data
        self.shared_data.update_data('normalized_objects', self.objects)
        self.init_variables()
        self.update()

    def set_new_connection(self, pos):
        #snapped_x, snapped_y = self.snap_to_grid(pos)
        pass

    def drawPreview(self, qp):
        if self.is_placing_object:
            mouse_pos = self.mapFromGlobal(self.cursor().pos())
            snapped_x, snapped_y = self.snap_to_grid(mouse_pos)
            
            # Convert back to screen coordinates
            screen_x = snapped_x * self.scale_factor + self.width() // 2
            screen_y = -snapped_y * self.scale_factor + self.height() // 2
            
            # Draw preview circle
            qp.setPen(QPen(Qt.black, 1, Qt.DashLine))
            qp.setBrush(Qt.transparent)
            qp.drawEllipse(screen_x - 5, screen_y - 5, 10, 10)
    
    #### Size stuff
    def sizeHint(self):
        # Provide a reasonable default size
        return QSize(600, 600)
    def minimumSizeHint(self):
        # Provide a minimum size that prevents compression
        return QSize(200, 200)
    def resizeEvent(self, event):
        # Handle resize events properly
        super().resizeEvent(event)
        # Adjust view if needed based on new size
        self.update()
    
    ### Rotate stuff
    def rotate_view(self, degrees):
        """Rotate the view by the specified degrees"""
        self.rotation_angle = (self.rotation_angle + degrees) % 360
        self.update()
        
    def set_rotation(self, degrees):
        """Set the absolute rotation angle"""
        self.rotation_angle = degrees % 360
        self.update()

    def get_rotation(self):
        """Get the current rotation angle"""
        return self.rotation_angle

    def transform_point(self, x, y):
        """Transform a point based on current view transformations (rotation, offset, scale)"""
        # Convert to widget coordinates
        widget_center_x = self.width() // 2
        widget_center_y = self.height() // 2
        
        # Apply scale and center
        screen_x = x * self.scale_factor + widget_center_x
        screen_y = -y * self.scale_factor + widget_center_y
        
        if self.rotation_angle != 0:
            # Create rotation transform
            transform = QTransform()
            transform.translate(widget_center_x, widget_center_y)
            transform.rotate(self.rotation_angle)
            transform.translate(-widget_center_x, -widget_center_y)
            
            # Apply rotation
            point = transform.map(QPointF(screen_x, screen_y))
            screen_x, screen_y = point.x(), point.y()
            
        return screen_x, screen_y

    def inverse_transform_point(self, screen_x, screen_y):
        """Convert screen coordinates back to grid coordinates, taking rotation into account"""
        widget_center_x = self.width() // 2
        widget_center_y = self.height() // 2
        
        # If there's rotation, inverse transform the point
        if self.rotation_angle != 0:
            transform = QTransform()
            transform.translate(widget_center_x, widget_center_y)
            transform.rotate(-self.rotation_angle)  # Note the negative angle for inverse
            transform.translate(-widget_center_x, -widget_center_y)
            
            point = transform.map(QPointF(screen_x, screen_y))
            screen_x, screen_y = point.x(), point.y()
        
        # Convert back to grid coordinates
        grid_x = (screen_x - widget_center_x - self.offset.x()) / self.scale_factor
        grid_y = -(screen_y - widget_center_y - self.offset.y()) / self.scale_factor
        
        return grid_x, grid_y