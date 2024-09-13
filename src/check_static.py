from collections import defaultdict
from src.check_fw_for_scheiben import *

helper_connection_dict = {
    'connection': ["Biegesteifecke", "Gelenk", "Normalkrafrgelenk", "Querkraftgelenk"],
    'feste_connection': ['Biegesteifecke'],
}

def find_repeated_nodes(connections):
    node_count = defaultdict(int)  # Dictionary to count occurrences of each node
    # Count the occurrences of each node
    for node1, node2 in connections:
        node_count[node1] += 1
        node_count[node2] += 1
    # Find nodes that appear more than once
    connection_nodes = [node for node, count in node_count.items() if count > 1]
    return connection_nodes
def categories_connection_nodes(conenctions, objects):

    #all_connection_nodes = find_repeated_nodes(conenctions) 
    scheiben_via_gelenke = detect_scheiben(conenctions)
    
    #### need to happen before the scheiben_via_gelenke, and should be passed and wokres as init scheiben
    scheiben = []
    for node in conenctions.keys():
        if objects[node[0]]['type'] in helper_connection_dict['feste_connection'] or objects[node[1]]['type'] in helper_connection_dict['feste_connection']:
            scheiben.append((node[0], node[1]))
    return scheiben_via_gelenke, scheiben


def test(conenctions, objects):
    scheiben_via_gelenke, scheiben = categories_connection_nodes(conenctions, objects)

    for scheibe in scheiben_via_gelenke:
        print("Scheibe via Gelenke:", scheibe)


