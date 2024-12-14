import json
import math
import numpy as np

def calculate_angle(x1, y1, x2, y2):
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return abs(angle) % 90   # For Normalization that don't have directionality
def calc_mean_angle(bin_idx, bin_edges, normalized_angles):
    bin_start = bin_edges[bin_idx]
    bin_end = bin_edges[bin_idx + 1]
    angles_in_bin = [angle for angle in normalized_angles if bin_start <= angle < bin_end]
    return np.mean(angles_in_bin) if angles_in_bin else None
def angle_difference(idx, target_angle, bin_edges, normalized_angles):
    mean_angle = calc_mean_angle(idx, bin_edges, normalized_angles)
    if mean_angle is None:
        return float('inf')  # Return infinity for empty bins
    return min(
        abs(mean_angle - target_angle),
        abs((mean_angle + 180) % 180 - target_angle)
    )

def get_coordinate_system_rotation(angles: list, bin_size=10):
    # Normalize angles
    normalized_angles = [angle % 180 for angle in angles]
    
    # Create histogram
    hist, bin_edges = np.histogram(normalized_angles, bins=np.arange(0, 181, bin_size))
    
    # Find all bins sorted by count
    sorted_indices = np.argsort(hist)[::-1]
    
    # Find primary angle (most common bin)
    primary_bin_idx = sorted_indices[0]
    primary_angle = calc_mean_angle(primary_bin_idx, bin_edges, normalized_angles)
    
    if primary_angle is None:
        raise ValueError("No valid angles found in the primary bin")
    
    # Calculate target angle for secondary (perpendicular to primary)
    target_angle = (primary_angle + 90) % 180
    
    # Find secondary angle (closest to perpendicular)
    secondary_bin_idx = min(
        [idx for idx in sorted_indices[1:] if calc_mean_angle(idx, bin_edges, normalized_angles) is not None],
        key=lambda idx: angle_difference(idx, target_angle, bin_edges, normalized_angles),
        default=None
    )

    if secondary_bin_idx is None:
        raise ValueError("No valid secondary angle found")
    
    secondary_angle = calc_mean_angle(secondary_bin_idx, bin_edges, normalized_angles)
    
    # Ensure the secondary angle is the one closer to being perpendicular
    if abs(secondary_angle - target_angle) > abs((secondary_angle + 90) % 180 - target_angle):
        secondary_angle = (secondary_angle + 90) % 180
    
    # Determine the rotation of the coordinate system
    rotation = min(primary_angle, secondary_angle)
    
    return {
        'rotation': rotation,
        'primary_axis': primary_angle,
        'secondary_axis': secondary_angle,
        'primary_bin_start': bin_edges[primary_bin_idx],
        'primary_bin_end': bin_edges[primary_bin_idx + 1],
        'secondary_bin_start': bin_edges[secondary_bin_idx],
        'secondary_bin_end': bin_edges[secondary_bin_idx + 1]
    }
def find_normalized_lengths(orianted_connections, tolerance=10.0):
    # get all but Diagonals
    sorted_lengths = sorted(
        [(key, conn['length']) if conn['orientation'] != 'diagonal' else (key, val)
         for key, conn in orianted_connections.items()
         for val in ([conn['length']] if conn['orientation'] != 'diagonal' else [conn['length_x'], conn['length_y']])
         ], key=lambda x: x[1]
    )

    base_length = sorted_lengths[0][1]  # Get smallest length as base

    for key, length in sorted_lengths:
        ratio = length / base_length
        rounded_ratio = round(ratio)
        if abs(ratio - rounded_ratio) <= tolerance:
            if orianted_connections[key]['orientation'] != 'diagonal':
                # For non-diagonal, save a single normalized length
                orianted_connections[key]['normalized_length'] = rounded_ratio
            else:
                # For diagonal, save normalized lengths for both x and y
                ratio_x = orianted_connections[key]['length_x'] / base_length
                ratio_y = orianted_connections[key]['length_y'] / base_length
                rounded_ratio_x = round(ratio_x)
                rounded_ratio_y = round(ratio_y)

                if abs(ratio_x - rounded_ratio_x) <= tolerance and abs(ratio_y - rounded_ratio_y) <= tolerance:
                    orianted_connections[key]['normalized_length_x'] = rounded_ratio_x
                    orianted_connections[key]['normalized_length_y'] = rounded_ratio_y

    return orianted_connections, base_length


def recognize_orientation(connections, primär_axis):
    lengths_of_primäre_axis,lengths_of_secondär_axis ,lengths_of_diagonals_primär,lengths_of_diagonals_secondär = [],[],[],[]
    for key, value in connections.items():
        length = value['length']
        angle = value['angle']   
        if abs(angle - primär_axis) <= 10:
            connections[key]['orientation'] = 'primär' 
            #lengths_of_primäre_axis.append(length)
        elif abs(angle - primär_axis) >= 80:
            lengths_of_secondär_axis.append(length)
            connections[key]['orientation'] = 'secondär' 
        else:
            normalized_length_x = abs(length * math.cos(math.radians(angle - primär_axis)))
            normalized_length_y = abs(length * math.sin(math.radians(angle - primär_axis)))
            connections[key]['orientation'] = 'diagonal' 
            connections[key]['length_x'] = normalized_length_x
            connections[key]['length_y'] = normalized_length_y
            #lengths_of_diagonals_primär.append(normalized_length_x)
            #lengths_of_diagonals_secondär.append(normalized_length_y)
    return connections

def normalize_angle(angle, common_angle):
    normalized_angle = (angle % 360 + 360) % 360
    normalized_common_angle = (common_angle % 360 + 360) % 360
    difference = normalized_angle - normalized_common_angle
    return abs(round(difference / 10) * 10)

def normalize_coordinate(coord, origin_coord, base_length):
    normalized = (coord - origin_coord) / base_length
    return round(normalized)

def find_bottom_right_object(objects):
    # Find the object with the smallest y-coordinate, and in case of a tie, the largest x-coordinate
    return min(objects.items(), key=lambda x: (x[1]['coordinates'][1], -x[1]['coordinates'][0]))

def analyze_connections(connections, objects):
    angles = [conn['angle'] for conn in connections.values()]
    common_angle_info = get_coordinate_system_rotation(angles)
    common_angle_axis1 = common_angle_info['primary_axis']

    orianted_connections = recognize_orientation(connections, common_angle_axis1)
    length_relationship_connections, base_length = find_normalized_lengths(orianted_connections)
    
    origin_id, origin_data = find_bottom_right_object(objects)
    origin_x, origin_y = origin_data['coordinates']

    # Create new normalized objects dictionary
    normalized_objects = {}
    for obj_id, obj_data in objects.items():
        x, y = obj_data['coordinates']
        normalized_objects[obj_id] = {
            'coordinates': (
                normalize_coordinate(x, origin_x, base_length),
                - normalize_coordinate(y, origin_y, base_length)    # Negate y-coordinate to match the coordinate system
            ),
            'type': obj_data['type'],
            'rotation': normalize_angle(obj_data['rotation'], common_angle_axis1) if 'rotation' in obj_data and obj_data['rotation'] != None else None,
        }

        ## Add connections to normalized objects if they exist
        if obj_data.keys().__contains__('connections'):
            normalized_objects[obj_id]['connections'] = obj_data['connections']
    
    
    return {
        'normalized_connections': length_relationship_connections,
        'base_length': base_length,
        'normalized_objects': normalized_objects,
        'origin_object': origin_id
    }

def get_normalization_from_path(label_path):
    with open(label_path, 'r') as file:
        data = json.load(file)
    return get_normalization(data)
    
    

def get_normalization(data):
    connections = {}
    for p1, p2 in data['connections']:
        x1, y1 = data['objects'][p1]['coordinates']
        x2, y2 = data['objects'][p2]['coordinates']
        
        angle = calculate_angle(x1, y1, x2, y2)
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        connections[(p1, p2)] = {'angle': angle, 'length': length}
    
    result = analyze_connections(connections, data['objects'])
    return result['normalized_objects'], result['normalized_connections']