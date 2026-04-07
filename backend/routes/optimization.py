from flask import Blueprint, request, jsonify, session
from database import get_db
from optimization import calculate_eoq, calculate_rop, dijkstra, calculate_total_cost

optimization_bp = Blueprint('optimization', __name__)


def _build_graph(db) -> dict:
    """
    Build a graph dict from transportation_routes table.
    Node labels are strings like 'S1', 'W2', 'R3'
    (Supplier/Warehouse/Retailer + their ID).
    """
    routes = db.execute('SELECT * FROM transportation_routes').fetchall()
    graph = {}
    for route in routes:
        src  = str(route['source_id'])
        dest = str(route['destination_id'])
        cost = route['cost']
        graph.setdefault(src,  {})[dest] = cost
        graph.setdefault(dest, {})[src]  = cost   # undirected
    return graph


@optimization_bp.route('/optimize', methods=['POST'])
def run_optimization():
    """
    Main optimization endpoint.

    Expected JSON body:
    {
        "demand":        1000,
        "ordering_cost": 50,
        "holding_cost":  2,
        "lead_time":     5,
        "start_node":    "1",   // optional, defaults to first supplier
        "end_node":      "3"    // optional, defaults to first retailer
    }
    """
    data = request.get_json()

    # ── Extract parameters ──
    D         = data.get('demand')
    S         = data.get('ordering_cost')
    H         = data.get('holding_cost')
    L         = data.get('lead_time')
    start_node = data.get('start_node')
    end_node   = data.get('end_node')

    if None in [D, S, H, L]:
        return jsonify({
            'error': 'demand, ordering_cost, holding_cost, and lead_time are required.'
        }), 400

    try:
        D, S, H, L = float(D), float(S), float(H), float(L)
    except (TypeError, ValueError):
        return jsonify({'error': 'All numeric fields must be valid numbers.'}), 400

    db = get_db()

    # ── Default nodes if not provided ──
    if start_node is None:
        first_supplier = db.execute('SELECT supplier_id FROM suppliers LIMIT 1').fetchone()
        start_node = str(first_supplier['supplier_id']) if first_supplier else '1'

    if end_node is None:
        first_retailer = db.execute('SELECT retailer_id FROM retailers LIMIT 1').fetchone()
        end_node = str(first_retailer['retailer_id']) if first_retailer else '3'

    # ── Calculations ──
    try:
        eoq = calculate_eoq(D, S, H)
    except ValueError as e:
        return jsonify({'error': f'EOQ error: {str(e)}'}), 400

    # Daily demand = annual demand / 365
    daily_demand = D / 365
    rop = calculate_rop(daily_demand, L)

    # Shortest path via Dijkstra
    graph = _build_graph(db)
    transport_cost, path = dijkstra(graph, start_node, end_node)

    if not path:
        return jsonify({
            'error': f'No route found from node {start_node} to node {end_node}.'
        }), 400

    path_str = ' → '.join(path)

    # Total cost
    total_cost = calculate_total_cost(D, S, H, transport_cost)

    # ── Save results to DB ──
    user_id = session.get('user_id', 1)   # default 1 if session not set
    db.execute(
        '''INSERT INTO results (user_id, eoq, rop, best_path, transport_cost, total_cost)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, eoq, rop, path_str, transport_cost, total_cost)
    )
    db.commit()

    return jsonify({
        'eoq':            eoq,
        'rop':            rop,
        'path':           path_str,
        'transport_cost': transport_cost,
        'total_cost':     total_cost
    }), 200
