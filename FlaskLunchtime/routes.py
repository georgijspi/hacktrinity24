from flask import Blueprint, render_template, session, redirect, url_for, request, send_file
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from forms import SignupForm, LoginForm
from database import db, User

# Define routes
def create_routes_blueprint(app):
    routes = Blueprint('routes', __name__)

    # Landing Page
    @routes.route("/")
    def index():
        return render_template("index.html")
    
    @routes.route("/signup", methods=["GET", "POST"])
    def signup():
        form = SignupForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('routes.login'))
        return render_template("signup.html", form=form)

    @routes.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        print("Login form: ", form)
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                print('Logged in successfully.', 'success')
                return redirect(url_for('routes.index'))
            else:
                flash('Invalid username or password.', 'danger')
        return render_template("login.html", form=form)

    @routes.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('routes.index'))
    
    return routes