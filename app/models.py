from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Attachment(db.Model):
	aid = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String(128), nullable=False)

class User_types(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)

class User(db.Model):
	uid = db.Column(db.Integer,  primary_key=True)
	login = db.Column(db.String(128), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	username = db.Column(db.String(128), nullable=False)
	cookie = db.Column(db.String(128), nullable=True)
	utype = db.Column(db.String(128), db.ForeignKey(User_types.id, ondelete="CASCADE"), nullable=False)
	photo = db.Column(db.String(128), db.ForeignKey(Attachment.aid, ondelete="CASCADE"), nullable=False, default='/')

	def __repr__(self):
		return f'<User {self.uid}>'


class Student(db.Model):
	id = db.Column(db.Integer, db.ForeignKey(User.uid), primary_key=True)
	group = db.Column(db.String(128), nullable=False)
	department = db.Column(db.String(128), nullable=False)


class Professor(db.Model):
	id = db.Column(db.Integer, db.ForeignKey(User.uid), primary_key=True)
	department = db.Column(db.String(128), nullable=False)


class Channel(db.Model):
	cid = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)
	photo = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"), nullable=False)


class User_Channel(db.Model):
	uid = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
	cid = db.Column(db.Integer, db.ForeignKey(Channel.cid, ondelete="CASCADE"), primary_key=True)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cid = db.Column(db.Integer, db.ForeignKey(Channel.cid, ondelete="CASCADE"), nullable=False)
	text = db.Column(db.String(128), nullable=False, default='')
	attachments = db.Column(db.Integer,db.ForeignKey(Attachment.aid, ondelete="CASCADE"),  nullable=True)
	author = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.Text, nullable=False, default='')
	author = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)
	attachments = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"),  nullable=True)
	date = db.Column(db.DateTime, nullable=False, default=datetime.now)

	def __repr__(self):
		return f'<Comment {self.comid}>'