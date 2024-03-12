from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from app import db
from app.models import Group, UserGroup, Invitation, Friendship, Event
from app.auth.models import User
from app.auth.forms import ICalForm
from icalParse import process_ical_file

from datetime import datetime
from flask import jsonify, request
from flask_login import login_required, current_user

api = Blueprint('api', __name__)

@api.route('/users/<int:user_id>/dashboard-data', methods=['GET'])
@login_required
def get_dashboard_data(user_id):
    # Ensure the requesting user is the same as the one logged in
    if current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Prepare the base data
    groups_data = [{'id': group.id, 'name': group.name} for group in current_user.groups]
    friendships = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
        Friendship.accepted == True
    ).all()
    
    friends_data = [{'id': friend.id, 'username': friend.username} for friend in 
                    [User.query.get(friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id) for friendship in friendships]]
    
    pending_requests_data = [{'id': req.id, 'username': User.query.get(req.user_id).username} for req in 
                             Friendship.query.filter(Friendship.friend_id == current_user.id, Friendship.accepted == False).all()]

    # Fetching event data
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if start_date and end_date:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        user_group_ids = [group.id for group in current_user.groups]
        events = Event.query.filter(
            (Event.start >= start_date) & (Event.end <= end_date) &
            ((Event.user_id == current_user.id) | (Event.group_id.in_(user_group_ids)))
        ).all()
    else:
        # Fetch all events if no date range is provided
        events = Event.query.filter(
            (Event.user_id == current_user.id) |
            (Event.group_id.in_([group.id for group in current_user.groups]))
        ).all()

    events_data = [{
        'id': event.id, 
        'title': event.title, 
        'start': event.start.isoformat(), 
        'end': event.end.isoformat(), 
        'color': 'yellow' if event.group_id is not None else ('blue' if event.user_id == current_user.id else 'green')
    } for event in events]

    # Combine all data into a single JSON response
    return jsonify({
        'pending_requests': pending_requests_data,
        'groups': groups_data,
        'friends': friends_data,
        'events': events_data  # Adding the events data to the response
    })


@api.route('/add-friend', methods=['POST'])
@login_required
def add_friend():
    username = request.json.get('username')
    if username == current_user.username:
        return jsonify({'error': 'Cannot add yourself as a friend'}), 400
    
    friend = User.query.filter_by(username=username).first()
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    existing_request = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend.id)) |
        ((Friendship.friend_id == current_user.id) & (Friendship.user_id == friend.id))
    ).first()
    
    if existing_request:
        return jsonify({'error': 'Friend request already sent or connection already exists'}), 400
    
    new_friendship = Friendship(user_id=current_user.id, friend_id=friend.id, accepted=False)
    db.session.add(new_friendship)
    db.session.commit()
    return jsonify({'message': 'Friend request sent'})

@api.route('/pending-requests', methods=['GET'])
@login_required
def pending_requests():
    pending = Friendship.query.filter_by(friend_id=current_user.id, accepted=False).all()
    pending_requests = [
        {'id': req.id, 'username': User.query.get(req.user_id).username} 
        for req in pending
    ]
    return jsonify(pending_requests=pending_requests), 200

@api.route('/accept-request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    friendship = Friendship.query.get(request_id)
    if not friendship:
        return jsonify({'error': 'Friend request not found.'}), 404
    if friendship.friend_id != current_user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403
    
    friendship.accepted = True
    db.session.commit()
    return jsonify({'message': 'Friend request accepted.'}), 200

@api.route('/deny-request/<request_id>', methods=['POST'])
@login_required
def deny_request(request_id):
    request = Friendship.query.get(request_id)
    if request and request.friend_id == current_user.id:
        db.session.delete(request)
        db.session.commit()
        return jsonify({'message': 'Friend request denied'}), 200
    return jsonify({'error': 'Request not found'}), 404

@api.route('/create-group', methods=['POST'])
@login_required
def create_group():
    data = request.json
    group_name = data.get('group_name')
    description = data.get('description')
    chatroom_link = data.get('chatroom_link')
    
    new_group = Group(name=group_name, description=description, chatroom_link=chatroom_link)
    db.session.add(new_group)
    db.session.commit()

    # Automatically add the creator to the group
    db.session.add(UserGroup(user_id=current_user.id, group_id=new_group.id))
    db.session.commit()

    return jsonify({'message': 'Group created successfully'}), 200

@api.route('/invite-to-group', methods=['POST'])
@login_required
def invite_to_group():
    data = request.json
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    if current_user not in group.users:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    user_to_invite = User.query.get(user_id)
    if not user_to_invite:
        return jsonify({'error': 'User not found'}), 404
    if user_to_invite in group.users:
        return jsonify({'error': 'User is already in the group'}), 400
    
    group.users.append(user_to_invite)
    db.session.commit()

    return jsonify({'message': f'User has been added to {group.name}'}), 200

@api.route('/get-friends-not-in-group/<int:group_id>', methods=['GET'])
@login_required
def get_friends_not_in_group(group_id):
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    if current_user not in group.users:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    all_friends = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
        Friendship.accepted == True
    ).all()
    
    friends_not_in_group = [{'id': friend.id, 'username': friend.username} 
                            for friendship in all_friends 
                            for friend in [User.query.get(friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id)] 
                            if friend not in group.users]
    
    return jsonify({'friends': friends_not_in_group}), 200

@api.route('/get-group-details/<int:group_id>', methods=['GET'])
@login_required
def get_group_details(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user not in group.users:
        return jsonify({'error': 'Unauthorized'}), 403
    
    members = [{'id': user.id, 'username': user.username} for user in group.users]
    group_details = {
        'name': group.name,
        'chatroom_link': group.chatroom_link,
        'members': members,
        'events': [{'title': event.title} for event in group.events]
    }
    return jsonify(group_details), 200

@api.route('/events', methods=['GET'])
@login_required
def events():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if start_date and end_date:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    
    user_group_ids = [group.id for group in current_user.groups]
    events = Event.query.filter(
        (Event.start >= start_date) & (Event.end <= end_date) & 
        ((Event.user_id == current_user.id) | (Event.group_id.in_(user_group_ids)))
    ).all()
    
    events_json = [{'id': event.id, 'title': event.title, 'start': event.start.isoformat(), 'end': event.end.isoformat(), 'color': 'blue' if event.user_id == current_user.id else 'green'} for event in events]
    return jsonify(events_json), 200

@api.route('/get-groups', methods=['GET'])
@login_required
def get_groups():
    groups = current_user.groups
    groups_data = [{'id': group.id, 'name': group.name} for group in groups]
    return jsonify(groups=groups_data), 200

@api.route('/add-event', methods=['POST'])
@login_required
def add_event():
    data = request.json
    if not all(key in data for key in ['title', 'start', 'end', 'group_id']):
        return jsonify({'error': 'Missing data'}), 400
    
    new_event = Event(
        title=data['title'],
        group_id=data['group_id'],
        start=datetime.fromisoformat(data['start']),
        end=datetime.fromisoformat(data['end']),
        user_id=current_user.id
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event added successfully!'}), 200

@api.route('/check-availability', methods=['POST'])
@login_required
def check_availability():
    data = request.json
    start = datetime.fromisoformat(data['start'])
    end = datetime.fromisoformat(data['end'])
    
    friends_query = db.session.query(Friendship.friend_id).filter(
        Friendship.user_id == current_user.id,
        Friendship.accepted == True
    )
    overlapping_events_query = db.session.query(Event.user_id).filter(
        Event.start < end,
        Event.end > start,
        Event.user_id.in_(friends_query)
    ).subquery()
    available_friends_query = friends_query.except_(db.session.query(overlapping_events_query.c.user_id))
    
    available_friends = User.query.filter(User.id.in_(available_friends_query)).all()
    available_friends_data = [{'id': friend.id, 'username': friend.username} for friend in available_friends]
    return jsonify(available_friends=available_friends_data), 200

@api.route('/upload-ical', methods=['POST'])
@login_required
def upload_ical():
    # Check if the post request has the file part
    if 'ical_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['ical_file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Ensure the file is in a supported format (e.g., 'ics')
        if not allowed_file(file.filename):
            return jsonify({'error': 'File format not supported'}), 400
        
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp_ical', filename)
        file.save(temp_path)

        # Here, call the function to process the uploaded iCal file.
        # This function should be adapted to your application's logic.
        # For example, it could parse the iCal file and create events in the database.
        process_ical_file(temp_path, current_user.id)

        # Clean up uploaded file
        os.remove(temp_path)

        return jsonify({'message': 'iCal imported successfully!'}), 200

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['ics']
