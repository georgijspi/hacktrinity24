from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from database import db, User
from routes import create_routes_blueprint

app = Flask(__name__)
app.config.from_pyfile('config.py')

csrf = CSRFProtect(app)
Session(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "routes.login"

app.register_blueprint(create_routes_blueprint(app))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)
