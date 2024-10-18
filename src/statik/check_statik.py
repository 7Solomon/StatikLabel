import math

def get_line_equation(coords, rotation):
    x, y = coords
    angle = math.radians(rotation)
    if rotation % 90 == 0:
        if rotation % 180 == 0:
            return ('horizontal', y)  # y = constant
        else:
            return ('vertical', x)  # x = constant
    else:
        # For 45-degree angles, we use the point-slope form: y - y1 = m(x - x1)
        slope = math.tan(angle)
        return ('diagonal', (slope, -slope * x + y))

def check_if_WL_and_node_meet(node, WL):
    node_coords = node['coordinates']
    wl_coords, wl_rotation = WL['coordinates'], WL['rotation']
    
    if node_coords == wl_coords:
        return True
    
    line = get_line_equation(wl_coords, wl_rotation)
    if line[0] == 'horizontal':
        return node_coords[1] == line[1]
    elif line[0] == 'vertical':
        return node_coords[0] == line[1]
    else:  # diagonal
        slope, intercept = line[1]
        return math.isclose(node_coords[1], slope * node_coords[0] + intercept, rel_tol=1e-9)

def check_if_WL_meets(data1, data2, data3):
    lines = [get_line_equation(data['coordinates'], data['rotation']) for data in (data1, data2, data3)]
    
    # Check for overlapping lines
    if data1['coordinates'] == data2['coordinates'] == data3['coordinates']:
        return True
    # Check for parallel lines
    if all(line[0] == 'horizontal' for line in lines) or all(line[0] == 'vertical' for line in lines):
        return len(set(line[1] for line in lines)) == 1
    
    # Check for intersection
    intersections = set()
    for i in range(3):
        for j in range(i + 1, 3):
            intersection = get_intersection(lines[i], lines[j])
            if intersection:
                intersections.add(intersection)
    
    # Check if the third line passes through the intersection point
    if len(intersections) == 1:
        intersection = intersections.pop()
        return all(check_point_on_line(intersection, line) for line in lines)
    
    return False

def get_intersection(line1, line2):
    if line1[0] == line2[0] == 'horizontal' or line1[0] == line2[0] == 'vertical':
        return None
    if line1[0] == 'horizontal':
        y = line1[1]
        if line2[0] == 'vertical':
            x = line2[1]
        else:
            slope, intercept = line2[1]
            x = (y - intercept) / slope
    elif line1[0] == 'vertical':
        x = line1[1]
        if line2[0] == 'horizontal':
            y = line2[1]
        else:
            slope, intercept = line2[1]
            y = slope * x + intercept
    else:
        if line2[0] == 'horizontal':
            y = line2[1]
            slope, intercept = line1[1]
            x = (y - intercept) / slope
        elif line2[0] == 'vertical':
            x = line2[1]
            slope, intercept = line1[1]
            y = slope * x + intercept
        else:
            slope1, intercept1 = line1[1]
            slope2, intercept2 = line2[1]
            if math.isclose(slope1, slope2, rel_tol=1e-9):
                return None
            x = (intercept2 - intercept1) / (slope1 - slope2)
            y = slope1 * x + intercept1
    return (x, y)

def check_point_on_line(point, line):
    x, y = point
    if line[0] == 'horizontal':
        return math.isclose(y, line[1], rel_tol=1e-9)
    elif line[0] == 'vertical':
        return math.isclose(x, line[1], rel_tol=1e-9)
    else:
        slope, intercept = line[1]
        return math.isclose(y, slope * x + intercept, rel_tol=1e-9)

def check_if_bestimmebar(i,j,k):
    return 3*i + 2*j + k
    
def check_if_fest_per_scheibe(value, objects):
    F_indexes = [index for index, d in enumerate(value) if d['type'] == 'F']
    P_indexes = [index for index, d in enumerate(value) if d['type'] == 'P']
    WL_indexes = [index for index, d in enumerate(value) if d['type'] == 'WL']
    f = check_if_bestimmebar(len(F_indexes),len(P_indexes),len(WL_indexes))
    if f > 3:
        raise ValueError('System ist Überbestimmt!!')       ## Falsche Logic kann auch mehr sein!!
    elif f < 3:
        return False
    elif f == 3:
        if len(F_indexes) == 1:
            return False
        if len(P_indexes) == 1 and len(WL_indexes) == 1:
            i,j = value[P_indexes[0]]['node'], value[WL_indexes[0]]['node']
            if check_if_WL_and_node_meet(objects[i],objects[j]):
                return False
            else:
                return True
        if len(WL_indexes) == 3:
            i ,j ,k = value[WL_indexes[0]]['node'],value[WL_indexes[1]['node']], value[WL_indexes[2]['node']]
            if check_if_WL_meets(objects[i],objects[j],objects[k]):
                return False
            else:
                return True

    else:
        raise ValueError('Fehler Hier, Format stimmt nicht!!')
    




def check_static_of_groud_scheiben(scheiben_pol_vals, objects):
    for key,scheiben_pol_value in scheiben_pol_vals.items():  ### Ist noch Falsch, bzw ineffizient, da es alle Pole anschaut nicht nur die (n,0)
            print(scheiben_pol_value)
            result = check_if_fest_per_scheibe(scheiben_pol_value,objects)


