from flask import Blueprint, render_template, session, redirect, url_for, request, send_file
from flask import flash, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import aliased

from dateutil.parser import parse
from datetime import datetime
import pytz
from icalendar import Calendar
import os

from forms import SignupForm, LoginForm, ICalForm
from database import db, User, Group, UserGroup, Event, Invitation, Friendship
from icalParse import process_ical_file

# Define routes
def create_routes_blueprint(app):
    routes = Blueprint('routes', __name__)

    # Landing Page
    @routes.route("/")
    def index():
        return render_template("index.html")
    
    @routes.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        ical_form = ICalForm()
        if ical_form.validate_on_submit():
            # Process file upload and event creation here
            filename = secure_filename(ical_form.ical_file.data.filename)
            temp_path = os.path.join('temp_ical', filename)
            ical_form.ical_file.data.save(temp_path)

            # Call function to process the uploaded iCal file
            process_ical_file(temp_path, current_user.id)

            # Clean up uploaded file
            os.remove(temp_path)
            flash('iCal imported successfully!', 'success')
            return redirect(url_for('routes.dashboard'))
        # Fetch groups the current user is part of
        groups = current_user.groups

        # Query to fetch friendships
        friendships = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
            Friendship.accepted == True
        ).all()

        # Resolve User objects from friendships
        friends = []
        for friendship in friendships:
            # If current user is the user_id in the friendship, add the friend user object
            if friendship.user_id == current_user.id:
                friends.append(User.query.get(friendship.friend_id))
            # If current user is the friend_id in the friendship, add the user user object
            else:
                friends.append(User.query.get(friendship.user_id))
        
        # Fetch pending friend requests
        pending_requests = Friendship.query.filter(
            Friendship.friend_id == current_user.id,
            Friendship.accepted == False
        ).all()

        return render_template('dashboard.html', ical_form=ical_form, groups=groups, friends=friends, pending_requests=pending_requests)
    # API endpoints
