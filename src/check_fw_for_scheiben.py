def detect_scheiben(connections):

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

    def expand_scheibe(scheibe):
        expanded = True
        while expanded:
            expanded = False
            for node in graph:
                if node not in scheibe:
                    connections = sum(1 for s in scheibe if node in graph[s])
                    if connections >= 2:
                        scheibe.add(node)
                        expanded = True
        return scheibe

    initial_scheiben = find_triangles()
    print(initial_scheiben)
    final_scheiben = [expand_scheibe(scheibe) for scheibe in initial_scheiben]

    # Merge overlapping Scheiben
    i = 0
    while i < len(final_scheiben):
        j = i + 1
        while j < len(final_scheiben):
            if not final_scheiben[i].isdisjoint(final_scheiben[j]):
                final_scheiben[i] = final_scheiben[i].union(final_scheiben[j])
                final_scheiben.pop(j)
            else:
                j += 1
        i += 1

    return final_scheiben


def get_graph(connections):
    # Create an adjacency list representation of the graph
    graph = {}
    for (node1, node2), _ in connections.items():
        if node1 not in graph:
            graph[node1] = set()
        if node2 not in graph:
            graph[node2] = set()
        graph[node1].add(node2)
        graph[node2].add(node1)
    return graph
def detect_scheiben(connections):
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

    def expand_scheibe(scheibe):
        expanded = True
        while expanded:
            expanded = False
            for node in graph:
                if node not in scheibe:
                    connections = sum(1 for s in scheibe if node in graph[s])
                    if connections >= 2:
                        scheibe.add(node)
                        expanded = True
        return scheibe

    initial_scheiben = find_triangles()
    if not initial_scheiben:
        # If no triangles found, return all nodes as separate sets
        return [{node} for node in graph]

    final_scheiben = [expand_scheibe(scheibe) for scheibe in initial_scheiben]

    # Merge overlapping Scheiben
    i = 0
    while i < len(final_scheiben):
        j = i + 1
        while j < len(final_scheiben):
            if not final_scheiben[i].isdisjoint(final_scheiben[j]):
                final_scheiben[i] = final_scheiben[i].union(final_scheiben[j])
                final_scheiben.pop(j)
            else:
                j += 1
        i += 1

    # Add remaining nodes as separate sets
    all_nodes = set(graph.keys())
    nodes_in_scheiben = set.union(*final_scheiben) if final_scheiben else set()
    isolated_nodes = all_nodes - nodes_in_scheiben
    final_scheiben.extend({node} for node in isolated_nodes)

    return final_scheiben

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
