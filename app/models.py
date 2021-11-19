from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):

	uid = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(128), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	# ...

	def __repr__(self):
		return f'<User {self.uid}>'


class Channel(db.Model):
	pass


class Post(db.Model):
	pass


class Message(db.Model):
	pass


class Comment(db.Model):
	comid = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.Text, nullable=False)
	author = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)
	date = db.Column(db.DateTime, default=datetime.now)
	# ...

	def __repr__(self):
		return f'<Comment {self.comid}>'