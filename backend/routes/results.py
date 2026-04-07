from flask import Blueprint, jsonify, session
from database import get_db

results_bp = Blueprint('results', __name__)


@results_bp.route('/', methods=['GET'])
def get_all_results():
    """Return all results for the logged-in user."""
    user_id = session.get('user_id', 1)
    db   = get_db()
    rows = db.execute(
        'SELECT * FROM results WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    return jsonify([dict(r) for r in rows]), 200


@results_bp.route('/latest', methods=['GET'])
def get_latest_result():
    """Return the most recent result for the logged-in user."""
    user_id = session.get('user_id', 1)
    db  = get_db()
    row = db.execute(
        'SELECT * FROM results WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    if row is None:
        return jsonify({'message': 'No results found.'}), 404
    return jsonify(dict(row)), 200


@results_bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    """Delete a specific result."""
    db = get_db()
    db.execute('DELETE FROM results WHERE result_id = ?', (result_id,))
    db.commit()
    return jsonify({'message': 'Result deleted.'}), 200
