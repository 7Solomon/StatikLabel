from collections import defaultdict, Counter
import itertools

import numpy as np
from src.statik.scheiben_detection import *


helper_connection_dict = {
    'wl_connection': ["Normalkraftgelenk", "Querkraftgelenk"],
    'connection': ["Biegesteifecke", "Gelenk", "Normalkraftgelenk", "Querkraftgelenk"],
    'feste_connection': ['Biegesteifecke'],
}

def _has_fixed_connection(from_node, to_node, objects):
    """
    Check if the from_node has a fixed connection to the to_node.
    """
    # Safely get connections, defaulting to empty list if node not found
    node_connections = objects.get(from_node, {}).get('connections', [])
    
    # Check if there's a fixed connection to the specific node
    return any(
        conn.get('type') == 'fest' and conn.get('to') == to_node 
        for conn in node_connections
    )

def find_scheiben_connections(scheiben, objects):   ### Vielleicht noch Falsch
    common_nodes_between_scheiben = {}
    for (i,set1), (j,set2) in itertools.combinations(scheiben.items(), 2):
        intersection = set1['nodes'].intersection(set2['nodes'])
        #print('DEBUG ', [objects[_]['type']for _ in intersection])
        if intersection:   # Just adds if exists
            common_nodes_between_scheiben[i, j] = [{'type':  'WL' if objects[_]['type'] in helper_connection_dict['wl_connection'] else 'P','node':_, 'rotation': objects[_].get('rotation', None) } for _ in intersection]      ### !!! Führt zu fehler, da connection auch Normal oder Querkraftgelenk sein kann
    return common_nodes_between_scheiben

def connect_overlapping_elements(connections, objects) ->list[set]:
    """ 
    die Function ist noch Falsch, da Beie Connection richutngen genommen werden,
    aber nur wenn to in die eine richtung kommt soll es Fest sein.
    """
    # Create a dictionary to store sets of connected elements
    connected_sets = []
    
    for i, (a, b) in enumerate(connections):
        if not connected_sets:              # Erster Durchlauf
            new_set = frozenset([a, b])
            connected_sets.append(new_set)
        else:
            test = set([a,b])

            for i, fset in enumerate(connected_sets):
                intersection=  set([a,b]) & fset 
                if intersection:
                    if any([_has_fixed_connection(common_node,ts, objects) for common_node in intersection for ts in test]):
                        connected_sets[i] = connected_sets[i] | frozenset([a, b])
                    else:
                        connected_sets.append(set([a, b]))
                else:
                    connected_sets.append(set([a, b]))
    return connected_sets

def categories_connection_nodes(conenctions, objects):
    ## Get all nodes that are fest connected
    feste_connection = []
    for (n1, n2) in conenctions.keys():
        if n2 in [_['to'] for _ in objects[n1]['connections'] if _['type'] == 'fest']:
            feste_connection.append((n1, n2))   
        if n1 in [_['to'] for _ in objects[n2]['connections'] if _['type'] == 'fest']:
            feste_connection.append((n2, n1))
    # Connect overlapping elements
    through_fest_connection_verbundene_scheiben = connect_overlapping_elements(feste_connection, objects)
    ## Get the Scheiben
    through_graph_detected_scheiben = detect_scheiben(conenctions, objects, initial_scheiben=through_fest_connection_verbundene_scheiben)
    return through_graph_detected_scheiben['final_scheiben']


def get_scheiben(conenctions, objects):
    """
    Detects Scheiben and then finds the connections between them so the nebenpole
    """
    foud_scheiben_sets = categories_connection_nodes(conenctions, objects)
    scheiben = {i+1:{"nodes": scheiben_data} for i, scheiben_data in enumerate(foud_scheiben_sets)}

    scheiben_connection = find_scheiben_connections(scheiben, objects)
    return {
        'scheiben_connection':scheiben_connection,
        'scheiben': scheiben,
        }




