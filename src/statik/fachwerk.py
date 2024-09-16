def get_graph(connections):
    graph = {}
    for (node1, node2), _ in connections.items():
        if node1 not in graph:
            graph[node1] = set()
        if node2 not in graph:
            graph[node2] = set()
        graph[node1].add(node2)
        graph[node2].add(node1)
    return graph

def detect_scheiben(connections, initial_scheiben=None):
    graph = get_graph(connections)

    def find_triangles():
        triangles = []
        for node in graph:
            neighbors = list(graph[node])
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    if neighbors[j] in graph[neighbors[i]]:
                        triangles.append({node, neighbors[i], neighbors[j]})
        return triangles

    def expand_scheibe(scheibe, processed_nodes):
        expanded = True
        while expanded:
            expanded = False
            new_nodes = set()
            for node in scheibe:
                if node not in processed_nodes:
                    for neighbor in graph[node]:
                        connections = sum(1 for s in scheibe if neighbor in graph[s])
                        if connections >= 2 and neighbor not in scheibe:
                            new_nodes.add(neighbor)
                    processed_nodes.add(node)
            if new_nodes:
                scheibe.update(new_nodes)
                expanded = True
        return scheibe

    triangles = find_triangles()
    
    if initial_scheiben:
        final_scheiben = [set(scheibe) for scheibe in initial_scheiben]
        final_scheiben.extend([set(triangle) for triangle in triangles])
    else:
        final_scheiben = [set(triangle) for triangle in triangles]

    if not final_scheiben:
        return {'final_scheiben': [{node} for node in graph], 'graph': graph}

    processed_nodes = set()
    expanded_scheiben = []

    for scheibe in final_scheiben:
        if not any(scheibe.issubset(existing) for existing in expanded_scheiben):
            expanded = expand_scheibe(scheibe, processed_nodes)
            if expanded not in expanded_scheiben:
                expanded_scheiben.append(expanded)

    all_nodes = set(graph.keys())
    nodes_in_scheiben = set.union(*expanded_scheiben) if expanded_scheiben else set()
    isolated_nodes = all_nodes - nodes_in_scheiben
    isolated_scheiben = [{node, *graph[node]} for node in isolated_nodes]
    expanded_scheiben.extend(isolated_scheiben)

    return {'final_scheiben': expanded_scheiben, 'graph': graph}