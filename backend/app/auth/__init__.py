from flask import Blueprint
from flask_login import LoginManager
# Import the User model from its module. Ensure the User class is correctly defined in .models
from .models import User

# Create a Blueprint for auth functionality
auth = Blueprint('auth', __name__)

# Setup Flask-Login's login manager
login_manager = LoginManager()

# Define user loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_auth_app(app):
    # Configure the login view
    login_manager.login_view = 'auth.login'
    # Initialize the login manager with the Flask app instance
    login_manager.init_app(app)

    # Register the auth Blueprint with the Flask app
    app.register_blueprint(auth, url_prefix='/auth')

    # Import the routes; this is done here to avoid circular imports.
    # Routes should be imported after the Blueprint is configured and registered.
    from . import routes
