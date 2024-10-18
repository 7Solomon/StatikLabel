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
    pole = []
    for node in scheibe['nodes']:
        pol = {}
        if objects[node]['type'] == 'Einspannung':
            pol['type'] = "F"
            pol['node'] = node
            pol['rotation'] = None

        if objects[node]['type'] == 'Normalkrafteinspannung':
            pol['type'] = "FWL"
            pol['node'] = node
            pol['rotation'] = objects[node]['rotation']
        
        if objects[node]['type'] == 'Querkrafteinspannung':
            pol['type'] = "FWL"
            pol['node'] = node
            pol['rotation'] = objects[node]['rotation']

        if objects[node]['type'] == 'Festlager':
            pol['type'] = "P"
            pol['node'] = node
            pol['rotation'] = None
        
        if objects[node]['type'] == 'Loslager': 
            pol['type'] = "WL"
            pol['node'] = node
            pol['rotation'] = objects[node]['rotation']
        pole.append(pol)
    pole = [_ for _ in pole if _.__len__() > 0]
    if len(pole) >0:
        return pole
    else:
        return None
    
def get_bind_pole(pole):
    new_disscoverd_pole = {}
    for i,((keya,keyb), value) in enumerate(pole.items()):
        for pol in value:
            if pol['type'] == 'P':
                for j, ((key2a,key2b), value2) in enumerate(pole.items()):
                    if i != j:    
                        if key2a == keya:
                            new_disscoverd_pole.setdefault((key2b, keyb),[]).append({'type': 'WL', 'node': value2[0]['node']})  # Mann kann auch value nehmen
                        if key2b == keya:
                            new_disscoverd_pole.setdefault((key2a, keyb),[]).append({'type': 'WL', 'node': value2[0]['node']})
                        if key2a == keyb:

                            new_disscoverd_pole.setdefault((key2b, keya),[]).append({'type': 'WL', 'node': value2[0]['node']})
                        if key2b == keyb:
                            new_disscoverd_pole.setdefault((key2a, keya),[]).append({'type': 'WL', 'node': value2[0]['node']})
                
    return new_disscoverd_pole

def combine_pole(pole1,pole2,pol3):
    combined_pole = pole1.copy()
    for key, value in pole2.items():
        if key in combined_pole:
            combined_pole[key].extend(value)
        else:
            combined_pole[key] = value
    
    for key, value in pol3.items():
        if key in combined_pole:
            combined_pole[key].extend(value)
        else:
            combined_pole[key] = value
    return combined_pole

def sort_poles_to_scheiben(pole):
    grouped = {}
    for key,vaulue in pole.items():
        for group_key in key:
            if group_key != 0:         # Wichtig für die (n,0) Pole das die nicht in die Gruppe kommen
                if group_key not in grouped:
                    grouped[group_key] = []
                if vaulue not in grouped[group_key]: 
                    grouped[group_key].extend(vaulue)
    return grouped
       


def get_all_pole(objects, scheiben, scheiben_connection):
    main_pole = {}
    for key,scheibe in scheiben.items():
        pol_element_of_scheibe = get_main_pole_from_object_data(objects, scheibe)
        if pol_element_of_scheibe is not None:
            main_pole[(key,0)] = pol_element_of_scheibe
    
    bind_pole = get_bind_pole(main_pole)     # Bind pole are the not trivial poles that comec from combination of two poles
    pole_of_scheiben = sort_poles_to_scheiben({**main_pole, **scheiben_connection})
    pole =  combine_pole(main_pole,bind_pole,scheiben_connection)
    return {
        'pole_of_scheiben':pole_of_scheiben,
        'pole': pole
    }
     