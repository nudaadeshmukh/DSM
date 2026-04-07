from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth import auth_bp
from routes.supply_chain import supply_chain_bp
from routes.optimization import optimization_bp
from routes.results import results_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'dsm_project.db'

CORS(app)

# Register blueprints
app.register_blueprint(auth_bp,         prefix='/api/auth')
app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
app.register_blueprint(optimization_bp, url_prefix='/api')
app.register_blueprint(results_bp,      url_prefix='/api/results')

# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
