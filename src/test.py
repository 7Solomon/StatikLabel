import json
import math
import numpy as np
from collections import defaultdict

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
   # print(secondary_bin_idx)
    
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
def find_length_relationships(orianted_connections, tolerance=10.0):
    # get all but Diagonals
    sorted_lengths = sorted(
        [conn['length'] if conn['oriantation'] != 'diagonal' else val 
            for conn in orianted_connections.values() 
            for val in ([conn['length']] if conn['oriantation'] != 'diagonal' else [conn['normalized_length_primär'], conn['normalized_length_secondär']])
            ]
    )
    base_length = sorted_lengths[0] # Get smallest length as base
    relationships = defaultdict(list)
    
    for length in sorted_lengths:
        ratio = length / base_length
        rounded_ratio = round(ratio)
        if abs(ratio - rounded_ratio) <= tolerance:
            relationships[rounded_ratio].append(length)
    
    return relationships, base_length

def recognize_oriantation(connections, primär_axis):
    lengths_of_primäre_axis,lengths_of_secondär_axis ,lengths_of_diagonals_primär,lengths_of_diagonals_secondär = [],[],[],[]
    #print(primär_axis)
    for key, value in connections.items():
        length = value['length']
        angle = value['angle']   
        if abs(angle - primär_axis) <= 10:
            connections[key]['oriantation'] = 'primär' 
            #lengths_of_primäre_axis.append(length)
        elif abs(angle - primär_axis) >= 80:
            lengths_of_secondär_axis.append(length)
            connections[key]['oriantation'] = 'secondär' 
        else:
            normalized_length_x = abs(length * math.cos(math.radians(angle - primär_axis)))
            normalized_length_y = abs(length * math.sin(math.radians(angle - primär_axis)))
            connections[key]['oriantation'] = 'diagonal' 
            connections[key]['normalized_length_primär'] = normalized_length_x
            connections[key]['normalized_length_secondär'] = normalized_length_y
            #lengths_of_diagonals_primär.append(normalized_length_x)
            #lengths_of_diagonals_secondär.append(normalized_length_y)
    return connections

def normalize_angle(angle, common_angle):
    return abs(angle - common_angle)
def normalize_coordinate(coord, origin_coord, base_length):
    normalized = (coord - origin_coord) / base_length
    #print(f"Original: {coord}, Origin: {origin_coord}, Base Length: {base_length}, Normalized: {normalized}")
    return round(normalized)

def find_bottom_left_object(objects):
    return min(objects.items(), key=lambda x: (x[1]['coordinates'][0], x[1]['coordinates'][1]))

def analyze_connections(connections, objects):
    angles = [conn['angle'] for conn in connections.values()]
    common_angle_info = get_coordinate_system_rotation(angles)
    common_angle_axis1 = common_angle_info['primary_axis']

    orianted_connections = recognize_oriantation(connections, common_angle_axis1)
    length_relationships, base_length = find_length_relationships(orianted_connections)
    
    origin_id, origin_data = find_bottom_left_object(objects)
    origin_x, origin_y = origin_data['coordinates']
    print(length_relationships)
    # Create new normalized connections dictionary
    normalized_connections = {}
    #for (p1, p2), conn in connections.items():
    #    normalized_connections[(p1, p2)] = {
    #        'angle': normalize_angle(conn['angle'], common_angle_axis1),
    #        'length': round(normalized_length / base_length, 2)
    #    }
    
    # Create new normalized objects dictionary
    normalized_objects = {}
    for obj_id, obj_data in objects.items():
        x, y = obj_data['coordinates']
        normalized_objects[obj_id] = {
            'coordinates': (
                normalize_coordinate(x, origin_x, base_length),
                normalize_coordinate(y, origin_y, base_length)
            ),
            'type': obj_data['type']
        }
    
    return {
        'common_angle_mean': common_angle_axis1,
        'base_length': base_length,
        'length_relationships': dict(length_relationships),
        'normalized_connections': normalized_connections,
        'normalized_objects': normalized_objects,
        'origin_object': origin_id
    }

def test():
    connections = {}
    with open('test.json', 'r') as file:
        data = json.load(file)
    
    for p1, p2 in data['connections']:
        x1, y1 = data['objects'][p1]['coordinates']
        x2, y2 = data['objects'][p2]['coordinates']
        
        angle = calculate_angle(x1, y1, x2, y2)
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        connections[(p1, p2)] = {'angle': angle, 'length': length}
    
    result = analyze_connections(connections, data['objects'])
    
    #print(f"Common angle: {result['common_angle_mean']:.2f} degrees")
    #print(f"Base length (L): {result['base_length']:.2f}")
    #print(f"Origin object: {result['origin_object']}")
    ##
    #print("\nLength relationships:")
    #for multiplier, lengths in result['length_relationships'].items():
    #    print(f"  {multiplier}L: {lengths}")
    ##
    #print("\nNormalized connections:")
    #for (p1, p2), conn in result['normalized_connections'].items():
    #    print(f"  {p1} - {p2}: Angle: {conn['angle']:.2f}, Length: {conn['length']}L")
    #
    #print("\nNormalized objects:")
    #for obj_id, obj_data in result['normalized_objects'].items():
    #    print(f"  {obj_id}: Coordinates: {obj_data['coordinates']}L, Type: {obj_data['type']}")
    return result['normalized_objects'], result['normalized_connections']
