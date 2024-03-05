from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords
    groups = db.relationship('Group', secondary='user_group', back_populates='users')
    friends = db.relationship('Friendship', back_populates='user', foreign_keys='Friendship.user_id')
    added_friends = db.relationship('Friendship', back_populates='friend', foreign_keys='Friendship.friend_id')

    def get_id(self):
        return self.id

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    chatroom_link = db.Column(db.String(200), nullable=True)
    users = db.relationship('User', secondary='user_group', back_populates='groups')
    events = db.relationship('Event', backref='group', lazy=True)

class UserGroup(db.Model):
    __tablename__ = 'user_group'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String(100), nullable=False, unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    invited_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group = db.relationship('Group', backref=db.backref('invitations', lazy=True))

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='friends')
    friend = db.relationship('User', foreign_keys=[friend_id], back_populates='added_friends')
    accepted = db.Column(db.Boolean, default=False, nullable=False)