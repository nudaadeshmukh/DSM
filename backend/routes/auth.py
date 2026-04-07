from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    confirm  = data.get('confirm_password', '')

    # Basic validation
    if not all([username, email, password, confirm]):
        return jsonify({'error': 'All fields are required.'}), 400
    if password != confirm:
        return jsonify({'error': 'Passwords do not match.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    db = get_db()

    # Check duplicates
    if db.execute('SELECT user_id FROM users WHERE username = ?', (username,)).fetchone():
        return jsonify({'error': 'Username already taken.'}), 409
    if db.execute('SELECT user_id FROM users WHERE email = ?', (email,)).fetchone():
        return jsonify({'error': 'Email already registered.'}), 409

    hashed = generate_password_hash(password)
    db.execute(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        (username, email, hashed)
    )
    db.commit()

    return jsonify({'message': 'Registration successful. Please log in.'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in an existing user."""
    data     = request.get_json()
    login_id = data.get('email_or_username', '').strip()
    password = data.get('password', '')

    if not login_id or not password:
        return jsonify({'error': 'Email/username and password are required.'}), 400

    db   = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE email = ? OR username = ?',
        (login_id, login_id)
    ).fetchone()

    if user is None or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    session['user_id']  = user['user_id']
    session['username'] = user['username']

    return jsonify({
        'message':  'Login successful.',
        'user_id':  user['user_id'],
        'username': user['username']
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out the current user."""
    session.clear()
    return jsonify({'message': 'Logged out successfully.'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    """Return currently logged-in user info."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated.'}), 401
    return jsonify({
        'user_id':  session['user_id'],
        'username': session['username']
    }), 200
