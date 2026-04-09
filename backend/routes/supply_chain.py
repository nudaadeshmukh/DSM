from flask import Blueprint, request, jsonify
from database import get_db, resolve_table_name

supply_chain_bp = Blueprint('supply_chain', __name__)


# ──────────────────────────────── SUPPLIERS ────────────────────────────────

@supply_chain_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    db  = get_db()
    rows = db.execute('SELECT * FROM suppliers').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/suppliers', methods=['POST'])
def add_supplier():
    data      = request.get_json()
    name      = data.get('name', '').strip()
    lead_time = data.get('lead_time')
    if not name or lead_time is None:
        return jsonify({'error': 'name and lead_time are required.'}), 400
    db = get_db()
    cur = db.execute(
        'INSERT INTO suppliers (name, lead_time) VALUES (?, ?)',
        (name, float(lead_time))
    )
    db.commit()
    return jsonify({'message': 'Supplier added.', 'supplier_id': cur.lastrowid}), 201


@supply_chain_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    data = request.get_json()
    db   = get_db()
    db.execute(
        'UPDATE suppliers SET name = ?, lead_time = ? WHERE supplier_id = ?',
        (data.get('name'), data.get('lead_time'), supplier_id)
    )
    db.commit()
    return jsonify({'message': 'Supplier updated.'}), 200


@supply_chain_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    db = get_db()
    db.execute('DELETE FROM suppliers WHERE supplier_id = ?', (supplier_id,))
    db.commit()
    return jsonify({'message': 'Supplier deleted.'}), 200


# ──────────────────────────────── WAREHOUSES ────────────────────────────────

@supply_chain_bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    db = get_db()
    rows = db.execute('SELECT * FROM warehouses').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/warehouses', methods=['POST'])
def add_warehouse():
    data     = request.get_json()
    name     = data.get('name', '').strip()
    location = data.get('location', '').strip()
    if not name or not location:
        return jsonify({'error': 'name and location are required.'}), 400
    db  = get_db()
    cur = db.execute(
        'INSERT INTO warehouses (name, location) VALUES (?, ?)',
        (name, location)
    )
    db.commit()
    return jsonify({'message': 'Warehouse added.', 'warehouse_id': cur.lastrowid}), 201


@supply_chain_bp.route('/warehouses/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    data = request.get_json()
    db   = get_db()
    db.execute(
        'UPDATE warehouses SET name = ?, location = ? WHERE warehouse_id = ?',
        (data.get('name'), data.get('location'), warehouse_id)
    )
    db.commit()
    return jsonify({'message': 'Warehouse updated.'}), 200


@supply_chain_bp.route('/warehouses/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    db = get_db()
    db.execute('DELETE FROM warehouses WHERE warehouse_id = ?', (warehouse_id,))
    db.commit()
    return jsonify({'message': 'Warehouse deleted.'}), 200


# ──────────────────────────────── RETAILERS ────────────────────────────────

@supply_chain_bp.route('/retailers', methods=['GET'])
def get_retailers():
    db = get_db()
    rows = db.execute('SELECT * FROM retailers').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/retailers', methods=['POST'])
def add_retailer():
    data     = request.get_json()
    name     = data.get('name', '').strip()
    location = data.get('location', '').strip()
    if not name or not location:
        return jsonify({'error': 'name and location are required.'}), 400
    db  = get_db()
    cur = db.execute(
        'INSERT INTO retailers (name, location) VALUES (?, ?)',
        (name, location)
    )
    db.commit()
    return jsonify({'message': 'Retailer added.', 'retailer_id': cur.lastrowid}), 201


@supply_chain_bp.route('/retailers/<int:retailer_id>', methods=['PUT'])
def update_retailer(retailer_id):
    data = request.get_json()
    db   = get_db()
    db.execute(
        'UPDATE retailers SET name = ?, location = ? WHERE retailer_id = ?',
        (data.get('name'), data.get('location'), retailer_id)
    )
    db.commit()
    return jsonify({'message': 'Retailer updated.'}), 200


@supply_chain_bp.route('/retailers/<int:retailer_id>', methods=['DELETE'])
def delete_retailer(retailer_id):
    db = get_db()
    db.execute('DELETE FROM retailers WHERE retailer_id = ?', (retailer_id,))
    db.commit()
    return jsonify({'message': 'Retailer deleted.'}), 200


# ──────────────────────────────── PRODUCTS ────────────────────────────────

@supply_chain_bp.route('/products', methods=['GET'])
def get_products():
    db = get_db()
    rows = db.execute('SELECT * FROM products').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/products', methods=['POST'])
def add_product():
    data          = request.get_json()
    name          = data.get('name', '').strip()
    holding_cost  = data.get('holding_cost')
    ordering_cost = data.get('ordering_cost')
    if not name or holding_cost is None or ordering_cost is None:
        return jsonify({'error': 'name, holding_cost, and ordering_cost are required.'}), 400
    db  = get_db()
    cur = db.execute(
        'INSERT INTO products (name, holding_cost, ordering_cost) VALUES (?, ?, ?)',
        (name, float(holding_cost), float(ordering_cost))
    )
    db.commit()
    return jsonify({'message': 'Product added.', 'product_id': cur.lastrowid}), 201


@supply_chain_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    db   = get_db()
    db.execute(
        'UPDATE products SET name=?, holding_cost=?, ordering_cost=? WHERE product_id=?',
        (data.get('name'), data.get('holding_cost'), data.get('ordering_cost'), product_id)
    )
    db.commit()
    return jsonify({'message': 'Product updated.'}), 200


@supply_chain_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    db = get_db()
    db.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    db.commit()
    return jsonify({'message': 'Product deleted.'}), 200


# ──────────────────────────────── INVENTORY ────────────────────────────────

@supply_chain_bp.route('/inventory', methods=['GET'])
def get_inventory():
    db = get_db()
    rows = db.execute('SELECT * FROM inventory').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/inventory', methods=['POST'])
def add_inventory():
    data          = request.get_json()
    location_id   = data.get('location_id', data.get('warehouse_id'))
    product_id    = data.get('product_id')
    demand        = data.get('demand')
    ordering_cost = data.get('ordering_cost')
    holding_cost  = data.get('holding_cost')
    lead_time     = data.get('lead_time')

    if None in [location_id, product_id, demand, ordering_cost, holding_cost, lead_time]:
        return jsonify({
            'error': 'warehouse_id/location_id, product_id, demand, ordering_cost, holding_cost, and lead_time are required.'
        }), 400

    db  = get_db()
    try:
        cur = db.execute(
            '''INSERT INTO inventory
               (location_id, product_id, demand, ordering_cost, holding_cost, lead_time)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (location_id, product_id, float(demand),
             float(ordering_cost), float(holding_cost), float(lead_time))
        )
    except Exception as exc:
        # Many existing schemas use `warehouse_id` instead of `location_id`.
        if "Unknown column 'location_id'" not in str(exc):
            raise
        cur = db.execute(
            '''INSERT INTO inventory
               (warehouse_id, product_id, demand, ordering_cost, holding_cost, lead_time)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (location_id, product_id, float(demand),
             float(ordering_cost), float(holding_cost), float(lead_time))
        )
    db.commit()
    return jsonify({'message': 'Inventory added.', 'inventory_id': cur.lastrowid}), 201


@supply_chain_bp.route('/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    db = get_db()
    db.execute('DELETE FROM inventory WHERE inventory_id = ?', (inventory_id,))
    db.commit()
    return jsonify({'message': 'Inventory record deleted.'}), 200


# ────────────────────────── TRANSPORTATION ROUTES ────────────────────────────

@supply_chain_bp.route('/routes', methods=['GET'])
def get_routes():
    db = get_db()
    routes_table = resolve_table_name(db, ['transportation_routes', 'routes'])
    rows = db.execute(f'SELECT * FROM {routes_table}').fetchall()
    return jsonify([dict(r) for r in rows]), 200


@supply_chain_bp.route('/routes', methods=['POST'])
def add_route():
    data           = request.get_json()
    source_id      = data.get('source_id')
    destination_id = data.get('destination_id')
    source_type    = data.get('source_type')
    destination_type = data.get('destination_type')
    cost           = data.get('cost')
    if None in [source_id, destination_id, cost] or not source_type or not destination_type:
        return jsonify({
            'error': 'source_id, destination_id, source_type, destination_type, and cost are required.'
        }), 400
    db  = get_db()
    routes_table = resolve_table_name(db, ['transportation_routes', 'routes'])
    try:
        cur = db.execute(
            f'''INSERT INTO {routes_table}
               (source_id, destination_id, source_type, destination_type, cost)
               VALUES (?, ?, ?, ?, ?)''',
            (source_id, destination_id, source_type, destination_type, float(cost))
        )
    except Exception as exc:
        # Existing schema fallback: routes(source, destination, cost)
        if "Unknown column 'source_id'" not in str(exc):
            raise
        cur = db.execute(
            f'''INSERT INTO {routes_table}
               (source, destination, cost)
               VALUES (?, ?, ?)''',
            (f"{source_type}{source_id}", f"{destination_type}{destination_id}", float(cost))
        )
    db.commit()
    return jsonify({'message': 'Route added.', 'route_id': cur.lastrowid}), 201


@supply_chain_bp.route('/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    db = get_db()
    routes_table = resolve_table_name(db, ['transportation_routes', 'routes'])
    db.execute(f'DELETE FROM {routes_table} WHERE route_id = ?', (route_id,))
    db.commit()
    return jsonify({'message': 'Route deleted.'}), 200
