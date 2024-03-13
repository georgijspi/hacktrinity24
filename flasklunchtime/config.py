# flask session configuration
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'your_very_secret_key_here'
