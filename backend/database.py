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
    if 'db' not in g:
        if current_app.config.get('DB_BACKEND') == 'mysql':

            # Step 1: Connect WITHOUT database
            temp_conn = pymysql.connect(
                host=current_app.config['MYSQL_HOST'],
                port=int(current_app.config['MYSQL_PORT']),
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                cursorclass=pymysql.cursors.DictCursor
            )

            temp_cursor = temp_conn.cursor()

            # Step 2: Create database if not exists
            db_name = current_app.config['MYSQL_DATABASE']
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

            temp_conn.commit()
            temp_conn.close()

            # Step 3: Connect WITH database
            raw_conn = pymysql.connect(
                host=current_app.config['MYSQL_HOST'],
                port=int(current_app.config['MYSQL_PORT']),
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=db_name,
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
    db = get_db()
    cursor = db.cursor()

    # Users table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS users (
            user_id   INT AUTO_INCREMENT PRIMARY KEY,
            username  VARCHAR(255) NOT NULL UNIQUE,
            email     VARCHAR(255) NOT NULL UNIQUE,
            password  VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Suppliers table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255) NOT NULL,
            lead_time   FLOAT NOT NULL
        )
    ''')

    # Warehouses table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
            name         VARCHAR(255) NOT NULL,
            location     VARCHAR(255) NOT NULL
        )
    ''')

    # Retailers table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS retailers (
            retailer_id INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255) NOT NULL,
            location    VARCHAR(255) NOT NULL
        )
    ''')

    # Products table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS products (
            product_id    INT AUTO_INCREMENT PRIMARY KEY,
            name          VARCHAR(255) NOT NULL,
            holding_cost  FLOAT NOT NULL,
            ordering_cost FLOAT NOT NULL
        )
    ''')

    # Inventory table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id  INT AUTO_INCREMENT PRIMARY KEY,
            location_id   INT NOT NULL,
            product_id    INT NOT NULL,
            demand        FLOAT NOT NULL,
            ordering_cost FLOAT NOT NULL,
            holding_cost  FLOAT NOT NULL,
            lead_time     FLOAT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Transportation routes table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS transportation_routes (
            route_id       INT AUTO_INCREMENT PRIMARY KEY,
            source_id      INT NOT NULL,
            destination_id INT NOT NULL,
            source_type    VARCHAR(255) NOT NULL,
            destination_type VARCHAR(255) NOT NULL,
            cost           FLOAT NOT NULL
        )
    ''')

    # Results table
    _execute(cursor, '''
        CREATE TABLE IF NOT EXISTS results (
            result_id      INT AUTO_INCREMENT PRIMARY KEY,
            user_id        INT NOT NULL,
            eoq            FLOAT,
            rop            FLOAT,
            best_path      TEXT,
            transport_cost FLOAT,
            total_cost     FLOAT,
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
