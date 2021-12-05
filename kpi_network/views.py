from flask import flash, session, request, render_template, make_response, send_from_directory
from datetime import datetime
from functools import wraps
from kpi_network.models import *
from kpi_network import app


@app.before_first_request
def before_first_request():
	populate_db()


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/session', methods=('GET', 'POST', 'DELETE'))
def session():
	# SECURITY NOTE: додати підписні flask-сесії до кукі
	if request.method == 'GET':
		# перевірити чи авторизований користувач
		cookies = request.cookies
		if cookies.get('uid'):
			return {
				'data': {'id': int(cookies['uid'])},
				'errors': []
			}, 200
		else:
			return {
				'data': {},
				'errors': ['User not found']
			}, 404

	elif request.method == 'POST':
		# авторизувати користувача та встановити кукі
		data = request.json
		login = data.get('login')
		password = data.get('password')
		user = User.query.filter_by(login=login, password=password).first()
		if user:
			res = {
				'data': {'id': user.uid},
				'errors': []
			}
			response = make_response(res, 200)
			response.set_cookie('uid', str(user.uid), max_age=None)
			return response
		else:
			return {
				'data': {},
				'errors': ['Invalid login or password']
			}, 401

	elif request.method == 'DELETE':
		# вийти з акаунту користувача
		res = {
			'data': {},
			'errors': []
		}
		response = make_response(res, 200)
		response.set_cookie('uid', '', max_age=None)
		return response


@app.route('/user', defaults={'uid': None}, methods=['POST', 'PUT', 'DELETE'])
@app.route('/user/<int:uid>', methods=['GET'])
def user(uid):
	# uid - id користувача
	if request.method == 'GET':
		# отримати інформацію по користувачу
		user = User.query.get(uid)
		if user:
			data = {
				'id': user.uid,
				'login': user.login,
				'name': user.name,
				'status': user.utype.name,
				'photo': user.photo.path
			}

			if user.utype_id == 1:  # student
				student = Student.query.get(uid)
				data['department'] = student.department
				data['group'] = student.group
			elif user.utype_id == 2:  # insturctor
				instructor = Instructor.query.get(uid)
				data['department'] = instructor.department

			return {'data': data, 'errors': []}, 200
		else:
			return {
				'data': {},
				'errors': ['User not found']
			}, 401
	elif request.method == 'POST':
		# створити нового користувача та встановити кукі
		data = request.json
		login = data.get('login')
		password = data.get('password')
		name = data.get('name')
		status = data.get('status')
		department = data.get('department')
		if status:
			if status.lower() in ['lecturer', 'instructor', 'teacher']:
				utype = 2
			elif status.lower() in ['student', 'undergraduate']:
				utype = 1
				group = data.get('group')
			else:
				return {
					'data': {},
					'errors': ['Unknown user type']
				}, 404
		else:
			return {
				'data': {},
				'errors': ['Bad request.']
			}, 400

		user_login = User.query.filter_by(login=login).first()
		if user_login:
			return {
				'data': {},
				'errors': ['Login already taken']
			}, 409

		new_user = User(login=login, password=password, name=name, utype_id=utype)
		db.session.add(new_user)
		db.session.commit()

		db.session.refresh(new_user)
		if utype == 1:
			new_student = Student(id=new_user.uid, group=group, department=department)
			db.session.add(new_student)
		elif utype == 2:
			new_instructor = Instructor(id=new_user.uid, department=department)
			db.session.add(new_instructor)

		db.session.commit()

		res = {
			'data': {'id': new_user.uid},
			'errors': []
		}
		response = make_response(res, 200)
		response.set_cookie('uid', str(new_user.uid), max_age=None)

		return response

	elif request.method == 'DELETE':
		# видалити користувача
		uid = request.cookies.get('uid')
		if not uid:
			return {
				'data': {'items': [], 'total': None},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		user = User.query.get(uid)
		db.session.delete(user)
		db.session.commit()

		res = {
			'data': {},
			'error': []
		}
		response = make_response(res, 200)
		response.set_cookie('uid', '', max_age=None)

		return response

	elif request.method == 'PUT':
		# оновити інформацію про користувача
		cookies = request.cookies
		uid = cookies.get('uid')
		if not uid:
			return {
				'data': {'items': [], 'total': None},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		user = User.query.get(uid)
		data = request.json

		for attr, value in data.items():
			setattr(user, attr, value)

		db.session.commit()
		return {
			'data': {},
			'errors': []
		}, 200


@app.route('/user/channels', methods=['GET'])
def user_channels():
	# отримати канали, на які підписаний користувач
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {'items': [], 'total': None},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	args = request.args
	page = args.get('page', 1)
	count = args.get('count', 5)
	channels = User_Channel.query.filter_by(uid=uid).all()
	channels_count = len(channels)
	if channels_count < count:
		channels_page = channels
	else:
		start = (page - 1) * count
		end = start + count
		channels_page = channels[start:end]

	items = []
	for c in channels_page:
		channel = c.channel
		items.append({
			'id': channel.cid,
			'name': channel.name,
			'photo': channel.photo.path
		})

	return {
		'data': {'items': items, 'total': len(items)},
		'errors': []
	}, 200


@app.route('/channel', defaults={'cid': None}, methods=['POST'])
@app.route('/channel/<int:cid>', methods=['GET', 'PUT', 'DELETE'])
def channel(cid):
	# cid - id каналу
	if request.method == 'GET':
		# отримати інформацію про канал

		# TODO перевіряти чи є користувач в мемберах каналу
		channel = Channel.query.get(cid)
		if channel:
			return {
				'data': {
					'id': channel.cid,
					'name': channel.name,
					'description': channel.description,
					'photo': channel.photo.path
				},
				'errors': []
			}, 200
		else:
			return {
				'data': {},
				'errors': ['Channel not found']
			}, 404

	elif request.method == 'POST':
		# створити новий канал
		uid = request.cookies.get('uid')
		if not uid:
			return {
				'data': {'items': [], 'total': None},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		data = request.json
		name = data.get('name')
		description = data.get('description', '')
		# photo_path = request.form['photo']
		# photo = Attachment(path=photo_path)
		# db.session.add(photo)

		# members = data.get('members')

		new_channel = Channel(name=name, description=description)
		db.session.add(new_channel)

		db.session.commit()
		db.session.refresh(new_channel)

		user_channel = User_Channel(uid=uid, cid=new_channel.cid, access_level=3)
		db.session.add(user_channel)

		db.session.commit()

		return {
			'data': {'id': new_channel.cid},
			'errors': []
		}, 200

	elif request.method == 'PUT':
		# оновити інформацію про канал
		channel = Channel.query.get(cid)
		if channel:
			data = request.json
			# photo = Attachment(path=photo_path)
			# db.session.add(photo)
			for attr, value in data.items():
				setattr(channel, attr, value)

			db.session.commit()

			return {
				'data': {},
				'errors': []
			}, 200
		else:
			return {
				'data': {},
				'errors': ['Channel not found']
			}, 404

	elif request.method == 'DELETE':
		# видалення каналу

		# TODO зробити можливість видалення тільки для овнера
		channel = Channel.query.get(cid)
		db.session.delete(channel)
		db.session.commit()

		return {
			'data': {},
			'error': []
		}, 200


@app.route('/channel/<int:cid>/members', methods=['GET'])
def channel_members(cid):
	# cid - id каналу
	# отримати список учасників каналу
	args = request.args
	page = args.get('page', 1)
	count = args.get('count', 5)
	users = User_Channel.query.filter_by(cid=cid).all()
	users_count = len(users)
	if users_count < count:
		users_page = users
	else:
		start = (page - 1) * count
		end = start + count
		users_page = users[start:end]

	items = []
	for u in users_page:
		user = u.user
		entry = {
			'id': user.uid,
			'login': user.login,
			'name': user.name,
			'status': user.utype.name,
			'photo': user.photo.path
		}

		if user.utype_id == 1:  # student
			student = Student.query.get(user.uid)
			entry['department'] = student.department
			entry['group'] = student.group
		elif user.utype_id == 2:  # insturctor
			instructor = Instructor.query.get(user.uid)
			entry['department'] = instructor.department
		items.append(entry)

	return {
		'data': {'items': items, 'total': len(items)},
		'errors': []
	}, 200

@app.route('/channel/<int:cid>/posts', methods=['GET'])
def channel_posts(cid):
	# cid - id каналу
	# отримати список постів даного каналу
	args = request.args
	page = args.get('page', 1)
	count = args.get('count', 5)
	posts = Post.query.filter_by(cid=cid).all()
	posts_count = len(posts)
	if posts_count < count:
		posts_page = posts
	else:
		start = (page - 1) * count
		end = start + count
		posts_page = posts[start:end]

	items = []
	for p in posts_page:
		entry = {
			'id': p.id,
			'text': p.text,
			'channelId': cid,
		}

		author = p.author
		author_entry = {
			'id': author.uid,
			'login': author.login,
			'name': author.name,
			'status': author.utype.name,
			'photo': author.photo.path
		}
		if author.utype_id == 1:  # student
			student = Student.query.get(author.uid)
			author_entry['department'] = student.department
			author_entry['group'] = student.group
		elif author.utype_id == 2:  # insturctor
			instructor = Instructor.query.get(author.uid)
			author_entry['department'] = instructor.department

		entry['author'] = author_entry
		items.append(entry)

	return {
		'data': {'items': items, 'total': len(items)},
		'errors': []
	}, 200


@app.route('/posts', defaults={'pid': None}, methods=['POST'])
@app.route('/posts/<int:pid>', methods=['GET', 'PUT', 'DELETE'])
def posts(pid):
	# pid - id посту
	if request.method == 'GET':
		# отримати інформацію про пост
		post = Post.query.get(pid)
		if post:
			data = {
				'id': post.id,
				'text': post.text,
				'channel': post.cid
			}
			author = post.author
			author_entry = {
				'id': author.uid,
				'login': author.login,
				'name': author.name,
				'status': author.utype.name,
				'photo': author.photo.path
			}
			if author.utype_id == 1:  # student
				student = Student.query.get(author.uid)
				author_entry['department'] = student.department
				author_entry['group'] = student.group
			elif author.utype_id == 2:  # instructor
				instructor = Instructor.query.get(author.uid)
				author_entry['department'] = instructor.department
			data['author'] = author_entry
			return {
				'data': data,
				'errors': []
			}, 200
		else:
			return {
				'data': {},
				'errors': ['Post not found']
			}, 400

	elif request.method == 'POST':
		# створити новий пост
		uid = request.cookies.get('uid')
		if not uid:
			return {
				'data': {'items': [], 'total': None},
				'errors': ['Unauthorized']
			}, 401

		uid = int(uid)
		data = request.json
		cid = data.get('cid')
		channel = Channel.query.get(cid)
		if not channel:
			return {
				'data': {},
				'errors': ['Specified channel does not exist']
			}, 404

		text = data.get('text')
		
		new_post = Post(text=text, cid=cid, author_id=uid)
		db.session.add(new_post)
		db.session.commit()
		return {
			'data': {'id': new_post.id},
			'errors': []
		}, 200


@app.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):
	# доступ до статичного файлу filename
	# https://flask.palletsprojects.com/en/2.0.x/api/#flask.send_from_directory
	return send_from_directory('static', filename)


if __name__ == "__main__":
	app.run(debug=True)