from flask import Blueprint, request, jsonify, session
from database import get_db, resolve_table_name
from optimization import (
    calculate_eoq,
    calculate_rop,
    dijkstra,
    annual_inventory_cost_breakdown,
)

optimization_bp = Blueprint('optimization', __name__)


def _product_lines_for_inventory(db, transport_cost: float) -> list:
    """
    One result row per inventory record, using that row's demand and costs.
    Transport cost is the shared path cost from the network optimization.
    """
    inv_rows = db.execute('SELECT * FROM inventory').fetchall()
    if not inv_rows:
        return []

    prod_rows = db.execute('SELECT product_id, name FROM products').fetchall()
    pid_to_name = {int(r['product_id']): r['name'] for r in prod_rows}

    lines = []
    for row in inv_rows:
        pid = int(row['product_id'])
        D = float(row['demand'])
        S = float(row['ordering_cost'])
        H = float(row['holding_cost'])
        L = float(row['lead_time'])
        loc = row['location_id'] if 'location_id' in row else None
        if loc is None and 'warehouse_id' in row:
            loc = row['warehouse_id']
        name = pid_to_name.get(pid, f'Product #{pid}')
        label = f'{name} (location {loc})' if loc is not None else name

        eoq = calculate_eoq(D, S, H)
        daily_demand = D / 365.0
        rop = calculate_rop(daily_demand, L)
        bd = annual_inventory_cost_breakdown(D, S, H, transport_cost)

        lines.append({
            'inventory_id': int(row['inventory_id']),
            'product_id': pid,
            'label': label,
            'product_name': name,
            'location_id': int(loc) if loc is not None else None,
            'eoq': eoq,
            'rop': rop,
            'transport_cost': bd['transport_cost'],
            'annual_ordering_cost': bd['annual_ordering_cost'],
            'annual_holding_cost': bd['annual_holding_cost'],
            'total_cost': bd['total_cost'],
        })
    return lines


def _summary_product_label(db) -> str:
    rows = db.execute('SELECT name FROM products ORDER BY product_id').fetchall()
    if len(rows) == 1:
        return rows[0]['name']
    return 'Optimization summary'


def _build_graph(db) -> dict:
    routes_table = resolve_table_name(db, ['transportation_routes', 'routes'])
    routes = db.execute(f'SELECT * FROM {routes_table}').fetchall()
    graph = {}

    for route in routes:
        # Support both schemas:
        # 1) transportation_routes(source_id, destination_id, source_type, destination_type, cost)
        # 2) routes(source, destination, cost)
        if 'source_type' in route and 'destination_type' in route:
            src = f"{route['source_type']}{route['source_id']}"
            dest = f"{route['destination_type']}{route['destination_id']}"
        else:
            src = str(route.get('source', ''))
            dest = str(route.get('destination', ''))

        cost = float(route['cost'])
        if not src or not dest:
            continue

        graph.setdefault(src,  {})[dest] = cost
        graph.setdefault(dest, {})[src]  = cost

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
        start_node = f"S{first_supplier['supplier_id']}"  if first_supplier else '1'

    if end_node is None:
        first_retailer = db.execute('SELECT retailer_id FROM retailers LIMIT 1').fetchone()
        end_node   = f"R{first_retailer['retailer_id']}" if first_retailer else '3'

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
    if not graph:
        transport_cost = 0.0
        breakdown = annual_inventory_cost_breakdown(D, S, H, transport_cost)
        total_cost = breakdown['total_cost']
        path_str = '— (add transportation routes in LogiBrain Data)'
        user_id = session.get('user_id', 1)
        db.execute(
            '''INSERT INTO results (user_id, eoq, rop, best_path, transport_cost, total_cost)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, eoq, rop, path_str, transport_cost, total_cost)
        )
        db.commit()
        product_lines = _product_lines_for_inventory(db, transport_cost)
        if not product_lines:
            slabel = _summary_product_label(db)
            product_lines = [{
                'inventory_id': None,
                'product_id': None,
                'label': slabel,
                'product_name': slabel,
                'location_id': None,
                'eoq': eoq,
                'rop': rop,
                'transport_cost': breakdown['transport_cost'],
                'annual_ordering_cost': breakdown['annual_ordering_cost'],
                'annual_holding_cost': breakdown['annual_holding_cost'],
                'total_cost': breakdown['total_cost'],
            }]
        return jsonify({
            'message': 'No routes in the database yet; EOQ/ROP are still computed.',
            'eoq': eoq,
            'rop': rop,
            'path': path_str,
            'best_path': path_str,
            'product_lines': product_lines,
            **breakdown,
        }), 200

    try:
        transport_cost, path = dijkstra(graph, start_node, end_node)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not path:
        return jsonify({
            'error': f'No route found from node {start_node} to node {end_node}.'
        }), 400

    path_str = ' → '.join(path)

    breakdown = annual_inventory_cost_breakdown(D, S, H, transport_cost)
    total_cost = breakdown['total_cost']

    # ── Save results to DB ──
    user_id = session.get('user_id', 1)   # default 1 if session not set
    db.execute(
        '''INSERT INTO results (user_id, eoq, rop, best_path, transport_cost, total_cost)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, eoq, rop, path_str, transport_cost, total_cost)
    )
    db.commit()

    product_lines = _product_lines_for_inventory(db, transport_cost)
    if not product_lines:
        slabel = _summary_product_label(db)
        product_lines = [{
            'inventory_id': None,
            'product_id': None,
            'label': slabel,
            'product_name': slabel,
            'location_id': None,
            'eoq': eoq,
            'rop': rop,
            'transport_cost': breakdown['transport_cost'],
            'annual_ordering_cost': breakdown['annual_ordering_cost'],
            'annual_holding_cost': breakdown['annual_holding_cost'],
            'total_cost': breakdown['total_cost'],
        }]

    return jsonify({
        'eoq':       eoq,
        'rop':       rop,
        'path':      path_str,
        'best_path': path_str,
        'product_lines': product_lines,
        **breakdown,
    }), 200
