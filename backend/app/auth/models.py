from flask_login import UserMixin

from ..models import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords
    groups = db.relationship('Group', secondary='user_group', back_populates='users')
    friends = db.relationship('Friendship', back_populates='user', foreign_keys='Friendship.user_id')
    added_friends = db.relationship('Friendship', back_populates='friend', foreign_keys='Friendship.friend_id')

    def get_id(self):
        return self.id
