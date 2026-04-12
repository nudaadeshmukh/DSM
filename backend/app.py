from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import init_db
from database import close_db
from routes.auth import auth_bp
from routes.supply_chain import supply_chain_bp
from routes.optimization import optimization_bp
from routes.results import results_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DB_BACKEND'] = os.getenv('DB_BACKEND', 'mysql').lower()
app.config['DATABASE'] = os.getenv('SQLITE_DB_PATH', 'dsm_project.db')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT'] = os.getenv('MYSQL_PORT', '3306')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE', '')
app.config['INIT_DB_ON_STARTUP'] = os.getenv('INIT_DB_ON_STARTUP', 'false').lower() == 'true'

CORS(app)

# Register blueprints
app.register_blueprint(auth_bp,         url_prefix='/api/auth')
app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
app.register_blueprint(optimization_bp, url_prefix='/api')
app.register_blueprint(results_bp,      url_prefix='/api/results')
app.teardown_appcontext(close_db)

# Optional DB bootstrap for fresh setups
if app.config['INIT_DB_ON_STARTUP']:
    with app.app_context():
        init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
