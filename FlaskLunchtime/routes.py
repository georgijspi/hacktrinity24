from flask import Blueprint, render_template, session, redirect, url_for, request, send_file
from flask import flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from forms import SignupForm, LoginForm
from database import db, User, Group, UserGroup, Event, Invitation, Friendship

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
        
    @routes.route('/dashboard')
    @login_required
    def dashboard():
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

        return render_template('dashboard.html', groups=groups, friends=friends, pending_requests=pending_requests)

    # API endpoints

    @routes.route('/fetch-dashboard-data', methods=['GET'])
    @login_required
    def fetch_dashboard_data():
        # Fetch groups the current user is part of
        groups_data = [{'id': group.id, 'name': group.name} for group in current_user.groups]

        # Fetch friendships
        friendships = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
            Friendship.accepted == True
        ).all()

        # Resolve User objects from friendships for friends list
        friends_data = [{'id': friend.id, 'username': friend.username} for friend in 
                        [User.query.get(friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id) for friendship in friendships]]

        # Fetch pending friend requests
        pending_requests_data = [{'id': req.id, 'username': User.query.get(req.user_id).username} for req in 
                                Friendship.query.filter(Friendship.friend_id == current_user.id, Friendship.accepted == False).all()]

        
        return jsonify({
            'pending_requests': pending_requests_data,  # List of dicts
            'groups': groups_data,  # List of dicts
            'friends': friends_data  # List of dicts
        }), 200


    @routes.route('/add-friend', methods=['POST'])
    @login_required
    def add_friend():
        username = request.form.get('username')
        if username == current_user.username:
            return jsonify({'message': 'Cannot add yourself as a friend'}), 400
        friend = User.query.filter_by(username=username).first()
        
        if not friend:
            return jsonify({'message': 'User not found'}), 404

        existing_request = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend.id)) |
            ((Friendship.friend_id == current_user.id) & (Friendship.user_id == friend.id))
        ).first()

        if existing_request:
            return jsonify({'message': 'Friend request already sent or connection already exists'}), 400

        new_friendship = Friendship(user_id=current_user.id, friend_id=friend.id, accepted=False)
        db.session.add(new_friendship)
        db.session.commit()
        return jsonify({'message': 'Friend request sent'}), 200


    @routes.route('/pending-requests', methods=['GET'])
    @login_required
    def pending_requests():
        pending = Friendship.query.filter_by(friend_id=current_user.id, accepted=False).all()
        pending_requests = [
            {'id': req.id, 'username': User.query.get(req.user_id).username} 
            for req in pending
        ]
        return jsonify(pending_requests=pending_requests), 200

    @routes.route('/accept-request/<int:request_id>', methods=['POST'])
    @login_required
    def accept_request(request_id):
        friendship = Friendship.query.get(request_id)
        if not friendship:
            return jsonify({'message': 'Friend request not found.'}), 404
        if friendship.friend_id != current_user.id:
            return jsonify({'message': 'Unauthorized action.'}), 403
        
        friendship.accepted = True
        db.session.commit()
        return jsonify({'message': 'Friend request accepted.'}), 200


    @routes.route('/deny-request/<request_id>', methods=['POST'])
    @login_required
    def deny_request(request_id):
        request = Friendship.query.get(request_id)
        if request and request.friend_id == current_user.id:
            db.session.delete(request)
            db.session.commit()
            return jsonify({'message': 'Friend request denied'}), 200
        return jsonify({'message': 'Request not found'}), 404


    @routes.route('/create-group', methods=['POST'])
    @login_required
    def create_group():
        group_name = request.form.get('group_name')
        description = request.form.get('description')
        # Logic to create a group
        new_group = Group(name=group_name, description=description)
        db.session.add(new_group)
        db.session.commit()
        # Automatically add the creator to the group
        db.session.add(UserGroup(user_id=current_user.id, group_id=new_group.id))
        db.session.commit()
        return jsonify({'message': 'Group created successfully'}), 200



    @routes.route('/invite-to-group', methods=['POST'])
    @login_required
    def invite_to_group():
        data = request.get_json()
        user_id = data.get('user_id')
        group_id = data.get('group_id')

        # Ensure the current user has the authority to invite users to the group
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'message': 'Group not found'}), 404

        if current_user not in group.users:
            return jsonify({'message': 'You are not a member of this group'}), 403

        # Find the user to invite
        user_to_invite = User.query.get(user_id)
        if not user_to_invite:
            return jsonify({'message': 'User not found'}), 404

        if user_to_invite in group.users:
            return jsonify({'message': 'User is already in the group'}), 400

        # Add the user to the group
        group.users.append(user_to_invite)
        db.session.commit()

        return jsonify({'message': f'User has been added to {group.name}'}), 200


    @routes.route('/get-friends-not-in-group/<int:group_id>', methods=['GET'])
    @login_required
    def get_friends_not_in_group(group_id):
        # Find the specified group
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'message': 'Group not found'}), 404
        
        # Ensure the current user is part of the group
        if current_user not in group.users:
            return jsonify({'message': 'You are not a member of this group'}), 403

        # Fetch all friends of the current user
        all_friends = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
            Friendship.accepted == True
        ).all()

        # Filter out friends who are already in the group
        friends_not_in_group = []
        for friendship in all_friends:
            friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
            friend = User.query.get(friend_id)
            
            # Check if this friend is not in the group
            if friend not in group.users:
                friends_not_in_group.append({'id': friend.id, 'username': friend.username})
        
        return jsonify({'friends': friends_not_in_group}), 200

    return routes