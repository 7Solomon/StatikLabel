import math
def calculate_intersection_point(origin1, angle1, origin2, angle2):
    # Convert angles to radians
    angle1_rad = math.radians(angle1)
    angle2_rad = math.radians(angle2)

    # Calculate the direction vectors for the two lines
    dir1_x, dir1_y = math.cos(angle1_rad), math.sin(angle1_rad)
    dir2_x, dir2_y = math.cos(angle2_rad), math.sin(angle2_rad)

    # Line equations: (x, y) = origin + t * direction
    # Solve for t1 and t2 where the lines intersect
    determinant = dir1_x * dir2_y - dir1_y * dir2_x
    if abs(determinant) < 1e-6:  # Lines are parallel or coincident
        return None

    dx = origin2[0] - origin1[0]
    dy = origin2[1] - origin1[1]

    t1 = (dx * dir2_y - dy * dir2_x) / determinant
    intersection_x = origin1[0] + t1 * dir1_x
    intersection_y = origin1[1] + t1 * dir1_y

    return (intersection_x, intersection_y)

def is_point_on_line(origin, rotation_angle, target_point, tolerance=1e-6):
    angle_rad = math.radians(rotation_angle)

    direction_x = math.cos(angle_rad)
    direction_y = math.sin(angle_rad)

    vector_x = target_point[0] - origin[0]
    vector_y = target_point[1] - origin[1]

    # Check if the cross product of the two vectors is approximately zero
    # Cross product for 2D vectors is |v1.x * v2.y - v1.y * v2.x|
    cross_product = abs(direction_x * vector_y - direction_y * vector_x)
    return cross_product < tolerance

def check_if_WL_colide(test_1, node_data,  tolerance=1e-6):
    origin1, angle1 = node_data[test_1[0]]['coordinates'], node_data[test_1[0]]['rotation']
    origin2, angle2 = node_data[test_1[1]]['coordinates'], node_data[test_1[1]]['rotation']
    origin3, angle3 = node_data[test_1[2]]['coordinates'], node_data[test_1[2]]['rotation']

    intersection = calculate_intersection_point(origin1, angle1, origin2, angle2)
    if intersection is None:
        return False  # First two lines do not intersect

    # Check if the third line passes through the intersection
    intersection_x, intersection_y = intersection

    # Convert the angle of the third line to radians
    angle3_rad = math.radians(angle3)
    dir3_x, dir3_y = math.cos(angle3_rad), math.sin(angle3_rad)

    # Vector from the third line's origin to the intersection point
    vector_x = intersection_x - origin3[0]
    vector_y = intersection_y - origin3[1]

    # Cross product between the direction vector and the vector to the intersection
    cross_product = abs(dir3_x * vector_y - dir3_y * vector_x)
    return cross_product < tolerance

def check_if_WL_and_point_meet(Wl_list, P_list, node_data):
    #if node_data is None:
    #    raise ValueError('node_data must be provided')
    if len(Wl_list) == 1:
        WL = Wl_list[0]
        P = P_list[0]

        Wl_start_koords = node_data[WL]['coordinates']
        wl_rotation = node_data[WL]['rotation']

        P_koords = node_data[P]['coordinates']
        return is_point_on_line(Wl_start_koords, wl_rotation, P_koords)
    else:
        P_koords = node_data[P]['coordinates']
        for WL in Wl_list:
            Wl_start_koords = node_data[WL]['coordinates']
            wl_rotation = node_data[WL]['rotation']
            
            if not is_point_on_line(Wl_start_koords, wl_rotation, P_koords):
                return False
        return True
        
            
