from collections import defaultdict
import itertools

import numpy as np
from src.statik.fachwerk import *


helper_connection_dict = {
    'connection': ["Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk"],
    'feste_connection': ['Biegesteifecke'],
}

test = {'Festlager': 'Hauptpol'}
def find_scheiben_connections(scheiben):
    common_nodes_between_scheiben = {}
    for (i,set1), (j,set2) in itertools.combinations(scheiben.items(), 2):
        intersection = set1['nodes'].intersection(set2['nodes'])
        common_nodes_between_scheiben[i, j] = {'node':intersection}
    return common_nodes_between_scheiben

def find_repeated_nodes(connections):
    node_count = defaultdict(int)  # Dictionary to count occurrences of each node
    # Count the occurrences of each node
    for node1, node2 in connections:
        node_count[node1] += 1
        node_count[node2] += 1
    # Find nodes that appear more than once
    connection_nodes = [node for node, count in node_count.items() if count > 1]
    return connection_nodes
def connect_overlapping_elements(connections, objects):
    # Create a dictionary to store sets of connected elements
    connected_sets = {}
    
    for i, (a, b) in enumerate(connections):
        # Find existing sets that contain either element
        existing_sets = [s for s in connected_sets if a in s or b in s]
        
        if not existing_sets:
            # If no existing sets, create a new one
            new_set = frozenset([a, b])
            connected_sets[new_set] = new_set
        else:
            # Check if the common element satisfies the condition
            common_element = a if any(a in s for s in existing_sets) else b
            if objects[common_element]['type'] in helper_connection_dict['feste_connection']:
                if len(existing_sets) == 1:
                    # If one existing set, add the new element to it
                    existing_set = existing_sets[0]
                    new_set = frozenset(existing_set | {a, b})
                    del connected_sets[existing_set]
                    connected_sets[new_set] = new_set
                else:
                    # If multiple existing sets, merge them
                    merged_set = frozenset(set.union(*(connected_sets[s] for s in existing_sets), {a, b}))
                    for s in existing_sets:
                        del connected_sets[s]
                    connected_sets[merged_set] = merged_set
            else:
                # If condition not met, add as a separate set
                new_set = frozenset([a, b])
                connected_sets[new_set] = new_set
    
    # Convert frozensets back to regular sets for the final result
    return [set(s) for s in connected_sets.values()]

def categories_connection_nodes(conenctions, objects):
    ## Dont know if needed
    feste_connection = []
    for node in conenctions.keys():
        if objects[node[0]]['type'] in helper_connection_dict['feste_connection'] or objects[node[1]]['type'] in helper_connection_dict['feste_connection']:
            feste_connection.append((node[0], node[1]))
    # Get scheiben from Biegesteifeecken
    scheiben = connect_overlapping_elements(feste_connection, objects)
    # Get scheiben from Fachwerk
    result = detect_scheiben(conenctions, initial_scheiben=scheiben)
    return result

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
    
def check_for_pole(scheibe, objects):
    # Check if pole is in the scheibe
    for node in scheibe['nodes']:
        if objects[node]['type'] == 'Festlager':
            scheibe['Hauptpol'] = node
    return scheibe



def get_scheiben(conenctions, objects):
    # Get Scheibe
    result = categories_connection_nodes(conenctions, objects)
    # scheiben data in schöne liste
    scheiben = {i+1:{"nodes": scheiben_data} for i, scheiben_data in enumerate(result['final_scheiben'])}
    scheiben_connection = find_scheiben_connections(scheiben)

    return {
        'scheiben_connection':scheiben_connection,
        'scheiben': scheiben,
        }




