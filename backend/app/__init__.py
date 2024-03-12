from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_cors import CORS

# Assuming db is initialized in app/models.py
from .models import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)

    CORS(app)

    csrf = CSRFProtect(app)
    Session(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Initialize and register the auth part of the app
    from .auth import init_auth_app
    init_auth_app(app)

    # Import and register other blueprints as needed, for example, the API blueprint
    from .api.routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app

app = create_app()
