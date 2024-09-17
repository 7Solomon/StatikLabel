import numpy as np
def is_point_on_line_np(p1, p2, p3):
    vec_p1_p2 = p2 - p1  # Vector from G to H
    vec_p1_p3 = p3 - p1  # Vector from G to D

    # Schaue ob die Punkte parralel sind
    cross_product = np.cross(vec_p1_p2, vec_p1_p3)
    
    # If the cross product is (approximately) 0, the points are collinear
    if np.isclose(cross_product, 0):
        # Schaue ob der Punkt auf der Linie liegt
        dot_product = np.dot(vec_p1_p3, vec_p1_p2)
        within_bounds = 0 <= dot_product <= np.dot(vec_p1_p2, vec_p1_p2)
        return within_bounds
    else:
        return False
    
def get_line_of_two_points(p1, p2):
    # Get the line between two points
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p1[1] - m * p1[0]
    return m, b

def is_point_on_line(m,b,p):
    return np.isclose(p[1], m * p[0] + b)

def get_main_pole_from_object_data(objects, scheibe):
    pole = {}
    for node in scheibe['nodes']:
        if objects[node]['type'] == 'Einspannung':
            pole['type'] = "F"
            pole['node'] = node
            pole['rotation'] = None

        if objects[node]['type'] == 'Normalkrafteinspannung':
            pole['type'] = "N"
            pole['node'] = node
            pole['rotation'] = objects[node]['rotation']
        
        if objects[node]['type'] == 'Querkrafteinspannung':
            pole['type'] = "Q"
            pole['node'] = node
            pole['rotation'] = objects[node]['rotation']

        if objects[node]['type'] == 'Festlager':
            pole['type'] = "HP"
            pole['node'] = node
            pole['rotation'] = None
            
        if objects[node]['type'] == 'Loslager': 
            pole['type'] = "HWL"
            pole['node'] = node
            pole['rotation'] = objects[node]['rotation']
 
    if len(pole) >0:
        return pole
    else:
        return None
    
def get_connection_pole_from_connection_data(objects, connection):
    print(connection)
    

def test(objects, scheiben, scheiben_connection):

    pole = {}
    for key,scheibe in scheiben.items():
        pol_element_of_scheibe = get_main_pole_from_object_data(objects, scheibe)
        if pol_element_of_scheibe is not None:
            pole[(key,0)] = pol_element_of_scheibe
    
    print(pole)
    get_connection_pole_from_connection_data(objects, scheiben_connection)