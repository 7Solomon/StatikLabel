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
    connecting_pols = []

    
    # Extract all direct WLs from pol_data
    for pol_pair, properties in pol_data.items():
        for prop in properties:
            if prop['type'] in ['WL', 'FWL']:
                node = prop['node']
                rotation = prop.get('rotation', None)
                
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
                    'id': pol_pair,
                    'node': node,
                    'type': prop['type'],
                    'rotation': rotation
                })


    connecting_pols = []
    processed_combinations = set()
    for pair1 in pol_data:
        # Skip if this pair doesn't contain any points
        if not any(p['type'] == 'P' for p in pol_data[pair1]):
            continue
            
        for pair2 in pol_data:
            # Skip if this pair doesn't contain any points
            if not any(p['type'] == 'P' for p in pol_data[pair2]):
                continue
                
            if pair1 == pair2 or (pair2, pair1) in processed_combinations:
                continue
                
            processed_combinations.add((pair1, pair2))
            
            # Get the poles
            p1_a, p1_b = pair1
            p2_a, p2_b = pair2
            
            # Find common pole
            common_poles = set([p1_a, p1_b]) & set([p2_a, p2_b])
            
            if common_poles:
                common_pole = common_poles.pop()
                
                # Get the non-common poles
                remaining_p1 = p1_a if p1_b == common_pole else p1_b
                remaining_p2 = p2_a if p2_b == common_pole else p2_b
                
                # Get the point nodes
                p1_node = next(p['node'] for p in pol_data[pair1] if p['type'] == 'P')
                p2_node = next(p['node'] for p in pol_data[pair2] if p['type'] == 'P')
                
                # Create new connection
                new_pair_id = tuple(sorted((remaining_p1, remaining_p2)))
                new_pair_node = [p1_node, p2_node]
                
                connecting_pols.append({
                    'id': new_pair_id,
                    'type': 'WL',
                    'node': new_pair_node
                })
    

    """# Check for pol intersections that should exist but don't
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
                    """

    return mismatches, weglinien, connecting_pols, len(mismatches) == 0