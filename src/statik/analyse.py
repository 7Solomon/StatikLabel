def analyze_polplan(pol_data, node_data):
    """
    Analyzes a polplan system for mismatches and extracts all Weglinien (WLs).
    
    Args:
        pol_data: Dictionary with pol pairs as keys and lists of their properties as values
        node_data: Dictionary with node information including coordinates and types
    
    Returns:
        tuple: (mismatches, weglinien, status)
            - mismatches: List of identified mismatches
            - weglinien: List of all WLs in the system
            - status: Boolean indicating if system is valid (True) or has mismatches (False)
    """
    mismatches = []
    weglinien = []
    
    # Helper function to create a WL identifier
    def create_wl_id(start_node, end_node):
        return f"WL_{start_node}_{end_node}"
    
    # Extract all direct WLs from pol_data
    for pol_pair, properties in pol_data.items():
        for prop in properties:
            if prop['type'] in ['WL', 'FWL']:
                node = prop['node']
                rotation = prop.get('rotation')
                
                # For FWL (Querkraftgelenk), we need to check perpendicular alignment
                if prop['type'] == 'FWL':
                    # Get node coordinates
                    node_coords = node_data[node]['coordinates']
                    
                    # Check if rotation matches node type
                    if node_data[node]['type'] == 'Querkraftgelenk':
                        expected_rotation = node_data[node]['rotation']
                        if rotation != expected_rotation:
                            mismatches.append({
                                'type': 'FWL_rotation_mismatch',
                                'node': node,
                                'expected': expected_rotation,
                                'actual': rotation
                            })
                
                weglinien.append({
                    'id': create_wl_id(pol_pair[0], pol_pair[1]),
                    'start_pol': pol_pair[0],
                    'end_pol': pol_pair[1],
                    'node': node,
                    'type': prop['type'],
                    'rotation': rotation
                })

    # Check for derived WLs through pol connections
    for pol1 in set([p[0] for p in pol_data.keys()]):
        for pol2 in set([p[1] for p in pol_data.keys()]):
            if pol1 != pol2:
                # Check if this combination creates a valid derived WL
                connecting_pols = []
                for pol_pair in pol_data.keys():
                    if pol1 in pol_pair and pol2 in pol_pair:
                        connecting_pols.append(pol_pair)
                
                if len(connecting_pols) == 2:
                    weglinien.append({
                        'id': create_wl_id(pol1, pol2),
                        'start_pol': pol1,
                        'end_pol': pol2,
                        'type': 'derived',
                        'derived_from': connecting_pols
                    })
    
    # Check for pol intersections that should exist but don't
    for wl1 in weglinien:
        for wl2 in weglinien:
            if wl1['id'] < wl2['id']:  # Avoid checking same pair twice
                # Check if these WLs should intersect based on mechanical constraints
                if (wl1['type'] != 'derived' and wl2['type'] != 'derived' and
                    wl1['start_pol'] != wl2['start_pol'] and
                    wl1['end_pol'] != wl2['end_pol']):
                    
                    # Check if intersection pol exists in system
                    intersection_found = False
                    expected_intersection = None
                    
                    # Calculate expected intersection based on geometry
                    # This would need actual coordinate calculations in a real implementation
                    
                    if not intersection_found and expected_intersection:
                        mismatches.append({
                            'type': 'missing_intersection',
                            'wl1': wl1['id'],
                            'wl2': wl2['id'],
                            'expected_pol': expected_intersection
                        })

    # Special handling for Normalkrafteinspannung
    for node, data in node_data.items():
        if data['type'] == 'Normalkrafteinspannung':
            # Check if corresponding WLs exist and are properly aligned
            normal_force_wls = [wl for wl in weglinien if wl['node'] == node]
            if not normal_force_wls:
                mismatches.append({
                    'type': 'missing_normal_force_wl',
                    'node': node
                })
            else:
                # Check alignment with rotation
                expected_rotation = data['rotation']
                for wl in normal_force_wls:
                    if wl['rotation'] != expected_rotation:
                        mismatches.append({
                            'type': 'normal_force_alignment_mismatch',
                            'node': node,
                            'wl': wl['id'],
                            'expected': expected_rotation,
                            'actual': wl['rotation']
                        })

    return mismatches, weglinien, len(mismatches) == 0