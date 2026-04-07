import math
import heapq


# ─────────────────────────────────────────────
# EOQ  —  Economic Order Quantity
# ─────────────────────────────────────────────
def calculate_eoq(D: float, S: float, H: float) -> float:
    """
    Calculate Economic Order Quantity.

    Args:
        D: Annual demand (units/year)
        S: Ordering cost per order ($)
        H: Holding cost per unit per year ($)

    Returns:
        EOQ value (float), rounded to 2 decimal places.

    Raises:
        ValueError: if any parameter is zero or negative.
    """
    if D <= 0 or S <= 0 or H <= 0:
        raise ValueError("D, S, and H must all be positive numbers.")
    eoq = math.sqrt((2 * D * S) / H)
    return round(eoq, 2)


# ─────────────────────────────────────────────
# ROP  —  Reorder Point
# ─────────────────────────────────────────────
def calculate_rop(d: float, L: float) -> float:
    """
    Calculate Reorder Point.

    Args:
        d: Average daily demand (units/day)
        L: Lead time in days

    Returns:
        ROP value (float), rounded to 2 decimal places.

    Raises:
        ValueError: if any parameter is negative.
    """
    if d < 0 or L < 0:
        raise ValueError("Daily demand and lead time must be non-negative.")
    rop = d * L
    return round(rop, 2)


# ─────────────────────────────────────────────
# Dijkstra's Shortest Path Algorithm
# ─────────────────────────────────────────────
def dijkstra(graph: dict, start: str, end: str) -> tuple[float, list]:
    """
    Find the shortest (cheapest) path between two nodes.

    Args:
        graph: Adjacency dict  { 'A': {'B': 10, 'C': 20}, 'B': {'C': 5}, ... }
        start: Source node name
        end:   Destination node name

    Returns:
        (total_cost, path_list)  e.g.  (15.0, ['A', 'B', 'C'])
        Returns (float('inf'), []) if no path exists.

    Raises:
        ValueError: if start or end node is not in the graph.
    """
    if start not in graph:
        raise ValueError(f"Start node '{start}' not found in graph.")
    if end not in graph:
        raise ValueError(f"End node '{end}' not found in graph.")

    # Min-heap: (cost, node)
    heap = [(0, start)]
    visited = set()
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}

    while heap:
        current_cost, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            if neighbor not in distances:
                distances[neighbor] = float('inf')
                previous[neighbor] = None

            new_cost = current_cost + weight
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = current_node
                heapq.heappush(heap, (new_cost, neighbor))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()

    if path[0] != start:
        return float('inf'), []          # No path found

    return round(distances[end], 2), path


# ─────────────────────────────────────────────
# Total Cost
# ─────────────────────────────────────────────
def calculate_total_cost(D: float, S: float, H: float,
                         transport_cost: float) -> float:
    """
    Total supply-chain cost = annual ordering cost
                             + annual holding cost
                             + transport cost.

    Annual ordering cost = (D / EOQ) * S
    Annual holding cost  = (EOQ / 2) * H
    """
    eoq = calculate_eoq(D, S, H)
    ordering_cost = (D / eoq) * S
    holding_cost  = (eoq / 2) * H
    total = ordering_cost + holding_cost + transport_cost
    return round(total, 2)
