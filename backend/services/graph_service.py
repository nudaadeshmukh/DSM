import heapq

def dijkstra(graph, start, end):
    """
    graph format:
    {
        'S1': {'W1': 10, 'R1': 20},
        'W1': {'R1': 5}
    }
    """

    queue = [(0, start, [])]  # (cost, node, path)
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == end:
            return cost, path

        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return float("inf"), []
