from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re

from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String)
    bio = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    posts = db.relationship('Post', backref='user')
    messages_sent = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='receiver', foreign_keys='Message.receiver_id')
    friends = db.relationship('Friend', backref='user')

    @validates('username')
    def validate_username(self, key, username):
        usernames = db.session.query(User.username).all()
        if not username:
            raise ValueError("Username required.")
        elif username in usernames:
            raise ValueError("Usernames must be unique.")
        return username
    
    @validates('email')
    def validate_email(self, key, email):
        emails = db.session.query(User.email).all()
        if not email:
            raise ValueError("Email address required.")
        elif '@' not in email:
            raise ValueError("Please enter a valid email address.")
        elif email in emails:
            raise ValueError("Email address must be unique.")
        return email
    
    @validates('password')
    def validate_password(self, key, password):
        if not password:
            raise ValueError("Password required.")
        elif 8 <= password <= 16:
            raise ValueError("Password must be between 8 and 16 characters long.")
        elif not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one capital letter.")
        elif not re.search(r'\d', password):
            raise ValueError("Password must contain at least one numeric character")
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character.")
        return password


class Post(db.Model, SerializerMixin):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    content = db.Column(db.String)
    title = db.Column(db.String)
    comments = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String)
    content = db.Column(db.String)
    status = db.Column(db.String)
    attachments = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Friend(db.Model, SerializerMixin):
    __tablename__ = 'friends'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', foreign_keys=[user_id])
    friend = db.relationship('User', foreign_keys=[friend_id])

    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id'),)

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Invalid user_id. User does not exist.")
        return user_id
    
    @validates('friend_id')
    def validate_friend_id(self, key, friend_id):
        friend = User.query.filter_by(id=friend_id).first()
        if not friend:
            raise ValueError("Invalid friend_id. User does not exist.")
        return friend_id