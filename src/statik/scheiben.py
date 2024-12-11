from collections import defaultdict
import itertools

import numpy as np
from src.statik.fachwerk import *


helper_connection_dict = {
    'wl_connection': ["Normalkraftgelenk", "Querkraftgelenk"],
    'connection': ["Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk"],
    'feste_connection': ['Biegesteifecke'],
}


def find_scheiben_connections(scheiben, objects):
    common_nodes_between_scheiben = {}
    for (i,set1), (j,set2) in itertools.combinations(scheiben.items(), 2):
        intersection = set1['nodes'].intersection(set2['nodes'])
        #print('DEBUG ', [objects[_]['type']for _ in intersection])
        if intersection:   # Just adds if exists
            common_nodes_between_scheiben[i, j] = [{'type':  'WL' if objects[_]['type'] in helper_connection_dict['wl_connection'] else 'P','node':_, 'rotation': objects[_].get('rotation', None) } for _ in intersection]      ### !!! Führt zu fehler, da connection auch Normal oder Querkraftgelenk sein kann
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
        print(node[0], node[1])
        print(objects[node[0]].get('connections'))
        if objects[node[0]]['type'] in helper_connection_dict['feste_connection'] or objects[node[1]]['type'] in helper_connection_dict['feste_connection']:
            feste_connection.append((node[0], node[1]))
    # Get scheiben from Biegesteifeecken
    scheiben = connect_overlapping_elements(feste_connection, objects)
    # Get scheiben from Fachwerk
    result = detect_scheiben(conenctions, initial_scheiben=scheiben)
    return result


def get_scheiben(conenctions, objects):
    # Get Scheibe
    result = categories_connection_nodes(conenctions, objects)
    # scheiben data in schöne liste
    scheiben = {i+1:{"nodes": scheiben_data} for i, scheiben_data in enumerate(result['final_scheiben'])}
    scheiben_connection = find_scheiben_connections(scheiben, objects)
    return {
        'scheiben_connection':scheiben_connection,
        'scheiben': scheiben,
        }




