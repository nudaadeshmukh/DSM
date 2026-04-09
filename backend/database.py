import sqlite3
import pymysql
from flask import g, current_app


class MySQLConnectionAdapter:
    """Adapter to provide sqlite-like execute() API on PyMySQL connections."""

    def __init__(self, connection):
        self._connection = connection

    def execute(self, query, params=()):
        query = query.replace('?', '%s')
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def cursor(self):
        return self._connection.cursor()

    def __getattr__(self, item):
        return getattr(self._connection, item)


def get_db():
    """Get DB connection for this request (MySQL or SQLite)."""
    if 'db' not in g:
        if current_app.config.get('DB_BACKEND') == 'mysql':
            raw_conn = pymysql.connect(
                host=current_app.config['MYSQL_HOST'],
                port=int(current_app.config['MYSQL_PORT']),
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DATABASE'],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            g.db = MySQLConnectionAdapter(raw_conn)
        else:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def _execute(cursor, query, params=()):
    """
    Execute query with compatible placeholders for selected backend.
    SQLite uses ? while MySQL drivers use %s.
    """
    if current_app.config.get('DB_BACKEND') == 'mysql':
        query = query.replace('?', '%s')
    return cursor.execute(query, params)


def init_db():
    """Create all tables if they don't exist (optional bootstrap)."""
    db = get_db()
    cursor = db.cursor()

    # Users table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTO_INCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            email     TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Suppliers table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name        TEXT    NOT NULL,
            lead_time   REAL    NOT NULL
        )
    ''')

    # Warehouses table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name         TEXT NOT NULL,
            location     TEXT NOT NULL
        )
    ''')

    # Retailers table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS retailers (
            retailer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name        TEXT NOT NULL,
            location    TEXT NOT NULL
        )
    ''')

    # Products table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS products (
            product_id    INTEGER PRIMARY KEY AUTO_INCREMENT,
            name          TEXT NOT NULL,
            holding_cost  REAL NOT NULL,
            ordering_cost REAL NOT NULL
        )
    ''')

    # Inventory table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id  INTEGER PRIMARY KEY AUTO_INCREMENT,
            location_id   INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            demand        REAL    NOT NULL,
            ordering_cost REAL    NOT NULL,
            holding_cost  REAL    NOT NULL,
            lead_time     REAL    NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Transportation routes table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS transportation_routes (
            route_id       INTEGER PRIMARY KEY AUTO_INCREMENT,
            source_id      INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            source_type    TEXT    NOT NULL,
            destination_type TEXT  NOT NULL,
            cost           REAL    NOT NULL
        )
    ''')

    # Results table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS results (
            result_id      INTEGER PRIMARY KEY AUTO_INCREMENT,
            user_id        INTEGER NOT NULL,
            eoq            REAL,
            rop            REAL,
            best_path      TEXT,
            transport_cost REAL,
            total_cost     REAL,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    db.commit()
    print("Database initialized successfully.")


def resolve_table_name(db, candidates):
    """
    Return the first existing table name from candidates.
    Falls back to the first candidate if none are found.
    """
    backend = current_app.config.get('DB_BACKEND')
    for table in candidates:
        if backend == 'mysql':
            row = db.execute('SHOW TABLES LIKE ?', (table,)).fetchone()
        else:
            row = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (table,)
            ).fetchone()
        if row:
            return table
    return candidates[0]
