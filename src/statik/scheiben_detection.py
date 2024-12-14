def get_graph(connections, objects):
    graph = {}
    for (node1, node2), _ in connections.items():
        if node1 not in graph:
            graph[node1] = {
                'neighbors': set(),
                #'info': objects[node1]
            }
        if node2 not in graph:
            graph[node2] = {
                'neighbors': set(),
                #'info': objects[node2]
            }
        graph[node1]['neighbors'].add(node2)
        graph[node2]['neighbors'].add(node1)
    return graph

def get_scheiben_from_lonely_nodes(graph):
    scheiben_list = set()
    for node in graph:
        #if not any(node in scheibe for scheibe in scheiben_list):      ### Ka was das soll, braucht man glaube nicht mehr, wenn da führt zu fehler
            scheiben = set([frozenset({node, _}) for _ in graph[node]['neighbors']])  ## frozenset für inmutable, da dann in anderes set
            scheiben_list.update(scheiben)
    return [set(_) for _ in scheiben_list]


def detect_scheiben(connections, objects, initial_scheiben=None):
    ## get graph tree
    graph = get_graph(connections, objects)
    
    def find_triangles():
        triangles = []
        for node in graph:
            neighbors = list(graph[node].keys())
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    # Check if the two neighbors are also connected
                    if neighbors[j] in graph[neighbors[i]]:
                        triangle = {node, neighbors[i], neighbors[j]}
                        triangles.append(triangle)
        return triangles
    def expand_scheibe(scheibe, processed_nodes):
        expanded = True
        while expanded:
            expanded = False
            new_nodes = set()
            for node in scheibe:
                if node not in processed_nodes:
                    for neighbor in graph[node]['neighbors']:
                        connections = sum(1 for s in scheibe if neighbor in graph[s]['neighbors'])
                        if connections >= 2 and neighbor not in scheibe:
                            new_nodes.add(neighbor)
                    processed_nodes.add(node)
            if new_nodes:
                scheibe.update(new_nodes)
                expanded = True
        return scheibe

    # Start with initial scheiben or triangles
    triangles = find_triangles()

    if initial_scheiben:
        # Addthe triangles to the scheiben
        final_scheiben = [set(scheibe) for scheibe in initial_scheiben]
        final_scheiben.extend([set(triangle) for triangle in triangles])
    else:
        # Nur die Dreiecke
        final_scheiben = [set(triangle) for triangle in triangles]

    if not final_scheiben:
        # Alle Nodes sind einzelne scheiben
        return {'final_scheiben': [set(_) for _ in get_scheiben_from_lonely_nodes(graph)], 'graph': graph}  

    processed_nodes = set()
    expa_scheiben = []

    for scheibe in final_scheiben:
        if not any(scheibe.issubset(existing) for existing in expa_scheiben):    
            expanded = expand_scheibe(scheibe, processed_nodes)
            if expanded not in expa_scheiben:
                expa_scheiben.append(expanded)


    all_nodes = set(graph.keys())
    nodes_in_scheiben = set.union(*expa_scheiben) if expa_scheiben else set()
    
    # Modify isolated nodes handling
    isolated_nodes = all_nodes - nodes_in_scheiben
    print('DEBUG isolated_nodes', isolated_nodes)
    isolated_graph = {node: graph[node] for node in isolated_nodes}
    print('DEBUG isolated_graph', isolated_graph)
    # Create scheiben for isolated nodes by adding their neighbors
    isolated_scheiben = get_scheiben_from_lonely_nodes(isolated_graph)
    expa_scheiben.extend([set(_) for _ in isolated_scheiben])
    return {'final_scheiben': expa_scheiben, 'graph': graph}