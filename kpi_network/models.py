from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from kpi_network import app
import os


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Attachment(db.Model):
	aid = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String(128), nullable=False)

class User_Types(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)

class User(db.Model):
	uid = db.Column(db.Integer,  primary_key=True)
	login = db.Column(db.String(128), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	name = db.Column(db.String(128), nullable=False)
	cookie = db.Column(db.String(128), nullable=True)
	utype_id = db.Column(db.Integer, db.ForeignKey(User_Types.id, ondelete="CASCADE"), nullable=False)
	utype = db.relationship(User_Types, backref='users')
	photo_id = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"), nullable=False, default=1)
	photo = db.relationship(Attachment)

	def __repr__(self):
		return f'<User {self.uid}>'


class Student(db.Model):
	id = db.Column(db.Integer, db.ForeignKey(User.uid), primary_key=True)
	group = db.Column(db.String(128), nullable=False)
	department = db.Column(db.String(128), nullable=False)


class Instructor(db.Model):
	id = db.Column(db.Integer, db.ForeignKey(User.uid), primary_key=True)
	department = db.Column(db.String(128), nullable=False)


class Channel(db.Model):
	cid = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), nullable=False)
	description = db.Column(db.String(128), nullable=True)
	photo_id = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"), nullable=False, default=2)
	photo = db.relationship(Attachment)


class User_Channel(db.Model):
	'''
	Access levels:
		0 - user (read, comment)
		1 - user (read, comment, post)
		2 - moderator (delete posts, ban/mute/add users)
		3 - owner (change channel info, give permissions, delete channel)
	'''
	uid = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
	cid = db.Column(db.Integer, db.ForeignKey(Channel.cid, ondelete="CASCADE"), primary_key=True)
	user = db.relationship(User)
	channel = db.relationship(Channel)
	access_level = db.Column(db.String(128), default=0, nullable=False)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cid = db.Column(db.Integer, db.ForeignKey(Channel.cid, ondelete="CASCADE"), nullable=False)
	channel = db.relationship(Channel, backref='posts')
	text = db.Column(db.String(128), nullable=False, default='')
	aid = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"),  nullable=True)
	attachment = db.relationship(Attachment)
	author_id = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)
	author = db.relationship(User, backref='posts')
	date = db.Column(db.DateTime, nullable=False, default=datetime.now)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.Text, nullable=False, default='')
	author_id = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)
	author = db.relationship(User, backref='comments')
	post_id = db.Column(db.Integer, db.ForeignKey(Post.id, ondelete="CASCADE"), nullable=False)
	post = db.relationship(Post, backref='comments')
	aid = db.Column(db.Integer, db.ForeignKey(Attachment.aid, ondelete="CASCADE"),  nullable=True)
	attachment = db.relationship(Attachment)
	date = db.Column(db.DateTime, nullable=False, default=datetime.now)

	def __repr__(self):
		return f'<Comment {self.comid}>'

def populate_db():
	db.create_all()
	if not User.query.first():
		import csv
		tables = {
			'Attachment': Attachment,
			'User_Types': User_Types,
			'User': User,
			'Student': Student,
			'Instructor': Instructor,
			'Channel': Channel,
			'User_Channel': User_Channel,
			'Post': Post,
			'Comment': Comment
		}

		for table, model in tables.items():
			with open(f'kpi_network/static/test_table_data/{table.lower()}.csv', 'r') as file:
				reader = csv.DictReader(file, delimiter=',')
				for row in reader:
					data = {k: v for k, v in row.items() if v}
					obj = model(**data)
					db.session.add(obj)
			db.session.commit()