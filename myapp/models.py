# myapp/models.py
from . import db
from flask_login import UserMixin
import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)  # Di produksi, gunakan hashing
    is_admin = db.Column(db.Boolean, default=False)

class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(255), nullable=False)  # URL RSS feed
    last_chapter = db.Column(db.String(50), default="")
    last_update = db.Column(db.DateTime, default=datetime.datetime.now)
    approved = db.Column(db.Boolean, default=False)
