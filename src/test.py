from collections import defaultdict
import json
import math
import numpy as np

def calculate_angle(x1, y1, x2, y2):
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return abs(angle) % 90   # For Normalization that don't have directionality

def get_most_common_angle(angles: list, bin_size=10):
    """
    Splits all angles in a Bucket of binSizes, and orders them to that bucket
    returns: a dictionary containing the mean of all angles in the bucket with the most angles in it,
             and the list of angles in that bin
    """
    hist, bin_edges = np.histogram(angles, bins=np.arange(0, 181, bin_size))
    most_common_bin_idx = np.argmax(hist) # Most Übereinstimmungen
    # Get boundaries
    if most_common_bin_idx == len(bin_edges) - 1:
        bin_start = bin_edges[most_common_bin_idx - 1]
        bin_end = bin_edges[most_common_bin_idx]
    else:
        bin_start = bin_edges[most_common_bin_idx]
        bin_end = bin_edges[most_common_bin_idx + 1]
    
    angles_in_bin = [angle for angle in angles if bin_start <= angle < bin_end]  # Get angles in Bin
    most_common_angle = np.mean(angles_in_bin) if angles_in_bin else None
    return {'mean': most_common_angle, 'inBin': angles_in_bin, 'bin_start': bin_start, 'bin_end': bin_end}

def find_length_relationships(lengths, tolerance=0.05):
    sorted_lengths = sorted(lengths)
    base_length = sorted_lengths[0]
    relationships = defaultdict(list)
    
    for length in sorted_lengths:
        ratio = length / base_length
        rounded_ratio = round(ratio)
        if abs(ratio - rounded_ratio) <= tolerance:
            relationships[rounded_ratio].append(length)
    
    return relationships, base_length

def normalize_diagonal_lengths(connections, common_angle):
    normalized_lengths = []
    for conn in connections.values():
        length = conn['length']
        angle = conn['angle']
        if abs(angle - common_angle) <= 5:  # Consider connections close to the common angle
            normalized_lengths.append(length)
        else:
            # Normalize diagonal length
            normalized_length = length * math.cos(math.radians(angle - common_angle))
            normalized_lengths.append(normalized_length)
    return normalized_lengths

def analyze_connections(connections):
    angles = [conn['angle'] for conn in connections.values()]
    common_angle_info = get_most_common_angle(angles)
    
    normalized_lengths = normalize_diagonal_lengths(connections, common_angle_info['mean'])
    length_relationships, base_length = find_length_relationships(normalized_lengths)
    
    return {
        'common_angle_mean': common_angle_info['mean'],
        'base_length': base_length,
        'length_relationships': dict(length_relationships)
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
    
    result = analyze_connections(connections)
    
    print(f"Common angle: {result['common_angle_mean']:.2f} degrees")
    print(f"Base length (L): {result['base_length']:.2f}")
    print("Length relationships:")
    for multiplier, lengths in result['length_relationships'].items():
        print(f"  {multiplier}L: {lengths}")

if __name__ == "__main__":
    test()