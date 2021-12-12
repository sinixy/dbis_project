from flask import flash, session, request, render_template, make_response, send_from_directory
from datetime import datetime
from functools import wraps
from kpi_network.models import *
from kpi_network import app
from base64 import b64decode
from io import BytesIO
from PIL import Image


@app.before_first_request
def before_first_request():
	populate_db()

def save_image(b64string, uid):
	starter = b64string.find(',')
	if starter == -1:
		return None
	try:
		image_data = bytes(b64string[starter+1:], encoding='ascii')
		with Image.open(BytesIO(b64decode(image_data))) as img:
			filename = f'{uid}_{int(datetime.now().timestamp())}.{img.format.lower()}'
			img.save(f'kpi_network/static/media/{filename}')
	except:
		return None
	return filename


@app.route('/api/session', methods=('GET', 'POST', 'DELETE'))
def session():
	# SECURITY NOTE: додати підписні flask-сесії до кукі
	if request.method == 'GET':
		# перевірити чи авторизований користувач
		cookies = request.cookies
		uid = cookies.get('uid')
		if uid:
			user = User.query.get(uid)
			if user:
				return {
					'data': {'id': int(cookies['uid'])},
					'errors': []
				}, 200
			else:
				return {
					'data': {},
					'errors': ['User does not exist']
				}, 200
		else:
			return {
				'data': {},
				'errors': ['No cookies']
			}, 200

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


@app.route('/api/user', defaults={'uid': None}, methods=['POST', 'PUT', 'DELETE'])
@app.route('/api/user/<int:uid>', methods=['GET'])
def user(uid):
	# uid - id користувача
	if request.method == 'GET':
		# отримати інформацію по користувачу
		user = User.query.get(uid)
		if user:
			current_uid = int(request.cookies.get('uid', 0))
			if current_uid == uid:
				isContact = None
			else:
				isContact = bool( Contacts.query.get((current_uid, uid)) )
			data = {
				'id': user.uid,
				'login': user.login,
				'name': user.name,
				'status': user.utype.name,
				'photo': app.config['BASE_URL'] + 'uploads/' + user.photo.path if user.photo else None,
				'isContact': isContact
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
		photo = data.get('photo')
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
		if photo:
			photo_path = save_image(photo, new_user.uid)
			if photo_path:
				new_photo = Attachment(path=photo_path)
				db.session.add(new_photo)
				db.session.commit()
				db.session.refresh(new_photo)
				photo_id = new_photo.aid
				new_user.photo_id = photo_id

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
				'data': {},
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
				'data': {},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		user = User.query.get(uid)

		data = request.json
		name = data.get('name')
		department = data.get('department')
		group = data.get('group')
		photo = data.get('photo')
		user.name = name
		if group:
			student = Student.query.get(uid)
			student.group = group
			student.department = department
		else:
			instructor = Instructor.query.get(uid)
			instructor.department = department

		if photo:
			photo_path = save_image(photo, uid)
			if photo_path:
				new_photo = Attachment(path=photo_path)
				db.session.add(new_photo)
				db.session.commit()
				db.session.refresh(new_photo)
				photo_id = new_photo.aid
				user.photo_id = photo_id

		db.session.commit()
		return {
			'data': {},
			'errors': []
		}, 200


@app.route('/api/user/channels', methods=['GET'])
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
	page = int(args.get('page', 1))
	count = int(args.get('count', 5))
	channels = User_Channel.query.filter_by(uid=uid)
	channels_count = channels.count()
	if channels_count < count:
		channels_page = channels.all()
	else:
		start = (page - 1) * count
		channels_page = channels.limit(count).offset(start).all()

	items = []
	for c in channels_page:
		channel = c.channel
		items.append({
			'id': channel.cid,
			'name': channel.name,
			'photo': app.config['BASE_URL'] + 'uploads/' + channel.photo.path if channel.photo else None
		})

	return {
		'data': {'items': items, 'total': channels_count},
		'errors': []
	}, 200


@app.route('/api/channel', defaults={'cid': None}, methods=['POST'])
@app.route('/api/channel/<int:cid>', methods=['GET', 'PUT', 'DELETE'])
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
					'photo': app.config['BASE_URL'] + 'uploads/' + channel.photo.path if channel.photo else None,
					'creatorId': User_Channel.query.filter_by(cid=channel.cid, access_level=1).first().uid,
					'members': [u.uid for u in User_Channel.query.filter_by(cid=cid).all()]
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
				'data': {},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		data = request.json
		name = data.get('name')
		description = data.get('description', '')
		photo = data.get('photo')
		members = data.get('members')

		new_channel = Channel(name=name, description=description)
		if photo:
			photo_path = save_image(photo, uid)
			if photo_path:
				new_photo = Attachment(path=photo_path)
				db.session.add(new_photo)
				db.session.commit()
				db.session.refresh(new_photo)
				photo_id = new_photo.aid
				new_channel.photo_id = photo_id

		db.session.add(new_channel)

		db.session.commit()
		db.session.refresh(new_channel)

		user_channel = User_Channel(uid=uid, cid=new_channel.cid, access_level=1)
		db.session.add(user_channel)
		if members:
			for m in members:
				db.session.add(User_Channel(uid=m, cid=new_channel.cid, access_level=0))

		db.session.commit()

		return {
			'data': {'id': new_channel.cid},
			'errors': []
		}, 200

	elif request.method == 'PUT':
		# оновити інформацію про канал
		uid = request.cookies.get('uid')
		if not uid:
			return {
				'data': {},
				'errors': ['Unauthorized']
			}, 401
		uid = int(uid)
		
		channel = Channel.query.get(cid)
		if channel:
			if uid != User_Channel.query.filter_by(cid=cid, access_level=1).first().uid:
				return {
					'data': {},
					'errors': ['Access denied']
				}, 200
			data = request.json
			name = data.get('name')
			description = data.get('description')

			members_request = data.get('members')
			members_in_channel = [u.uid for u in User_Channel.query.filter_by(cid=cid).all()]
			members_to_delete = set(members_in_channel) - set(members_request)
			members_to_add = set(members_request) - set(members_in_channel)

			photo = data.get('photo')
			if photo:
				photo_path = save_image(photo, uid)
				if photo_path:
					new_photo = Attachment(path=photo_path)
					db.session.add(new_photo)
					db.session.commit()
					db.session.refresh(new_photo)
					photo_id = new_photo.aid
					channel.photo_id = photo_id

			channel.name = name
			channel.description = description

			for m in members_to_add:
				db.session.add(User_Channel(uid=m, cid=cid, access_level=0))
			for m in members_to_delete:
				if m == uid:
					continue
				user_channel_to_delete = User_Channel.query.get((m, cid))
				if user_channel_to_delete:
					db.session.delete(user_channel_to_delete)

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


@app.route('/api/channel/<int:cid>/posts', methods=['GET'])
def channel_posts(cid):
	# cid - id каналу
	# отримати список постів даного каналу
	args = request.args
	page = int(args.get('page', 1))
	count = int(args.get('count', 5))
	posts = Post.query.filter_by(cid=cid).order_by(Post.date.desc())
	posts_count = posts.count()
	if posts_count < count:
		posts_page = posts.all()
	else:
		start = (page - 1) * count
		posts_page = posts.limit(count).offset(start).all()

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
			'photo': app.config['BASE_URL'] + 'uploads/' + author.photo.path if author.photo else None
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
		'data': {'items': items, 'total': posts_count},
		'errors': []
	}, 200


@app.route('/api/posts', defaults={'pid': None}, methods=['POST'])
@app.route('/api/posts/<int:pid>', methods=['GET', 'PUT', 'DELETE'])
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
				'photo': app.config['BASE_URL'] + 'uploads/' + author.photo.path if author.photo else None
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
				'data': {},
				'errors': ['Unauthorized']
			}, 401

		uid = int(uid)
		data = request.json
		cid = data.get('channelId')
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


@app.route('/api/search', methods=['GET'])
def search():
	# пошук користувача по логіну або імені
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {'items': [], 'total': None},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	args = request.args
	q = args.get('query')
	page = int(args.get('page', 1))
	count = int(args.get('count', 5))
	if q:
		# 1 - тільки контакти, 2 - только не контакти, 0 - усі
		search_type = int(args.get('contact', 0))
		res_raw = User.query.msearch(q, fields=['login', 'name']).all()
		user_contacts = [i.uid_2 for i in Contacts.query.filter_by(uid_1=uid).all()]
		if search_type == 0:
			# шукати серед усіх користувачів
			res = res_raw
		elif search_type == 1:
			# шукати лише серед контактів
			res = []
			for u in res_raw:
				if u.uid in user_contacts:
					res.append(u)
		elif search_type == 2:
			# шукати серед усіх користувачів, окрім контактів
			res = []
			for u in res_raw:
				if u.uid not in user_contacts:
					res.append(u)
		else:
			return {
				'data': {},
				'errors': ['Invalid contact value']
			}

		total = len(res)

		if total < count:
			res_page = res
		else:
			start = (page - 1) * count
			end = start + count
			res_page = res[start:end]
	else:
		res = User.query.msearch(q, fields=['login', 'name'])
		total = res.count()
		start = (page - 1) * count
		res_page = res.limit(count).offset(start).all()

	items = []
	for u in res_page:
		if uid == u.uid:
			isContact = None
		else:
			isContact = bool( Contacts.query.get((uid, u.uid)) )
		entry = {
			'id': u.uid,
			'login': u.login,
			'name': u.name,
			'status': u.utype.name,
			'photo': app.config['BASE_URL'] + 'uploads/' + u.photo.path if u.photo else None,
			'isContact': isContact
		}

		if u.utype_id == 1:  # student
			student = Student.query.get(u.uid)
			entry['department'] = student.department
			entry['group'] = student.group
		elif u.utype_id == 2:  # insturctor
			instructor = Instructor.query.get(u.uid)
			entry['department'] = instructor.department
		items.append(entry)
	return {
		'data': {
			'items': items,
			'total': total
		},
		'errors': []
	}, 200

@app.route('/api/user/contacts', methods=['GET'])
def user_contacts():
	# отримати контакти користувача
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {'items': [], 'total': None},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	args = request.args
	page = int(args.get('page', 1))
	count = int(args.get('count', 5))
	contacts = Contacts.query.filter_by(uid_1=uid)
	contacts_count = contacts.count()
	if contacts_count < count:
		contacts_page = contacts.all()
	else:
		start = (page - 1) * count
		contacts_page = contacts.limit(count).offset(start).all()

	items = []
	for uc in contacts_page:
		user = User.query.get(uc.uid_2)
		entry = {
			'id': user.uid,
			'login': user.login,
			'name': user.name,
			'status': user.utype.name,
			'photo': app.config['BASE_URL'] + 'uploads/' + user.photo.path if user.photo else None
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
		'data': {
			'items': items,
			'total': contacts_count
		},
		'errors': []
	}, 200



@app.route('/api/contact/<int:contact_id>', methods=['POST', 'DELETE'])
def contact(contact_id):
	# contact_id - ID контакту
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	if uid == contact_id:
		return {
			'data': {},
			'errors': ["Get a life bro"]
		}, 200

	user_contacts = [i.uid_2 for i in Contacts.query.filter_by(uid_1=uid).all()]

	if request.method == 'POST':
		# додати новий контакт
		if contact_id in user_contacts:
			return {
				'data': {},
				'errors': ['Contact alredy exists']
			}, 200

		new_contact_1 = Contacts(uid_1=uid, uid_2=contact_id)
		new_contact_2 = Contacts(uid_1=contact_id, uid_2=uid)
		db.session.add(new_contact_1)
		db.session.add(new_contact_2)
		db.session.commit()
		return {
			'data': {},
			'errors': []
		}, 200

	elif request.method == 'DELETE':
		# видалити контакт
		if contact_id not in user_contacts:
			return {
				'data': {},
				'errors': ['Contact does not exist']
			}, 200
		contact_1 = Contacts.query.get((uid, contact_id))
		contact_2 = Contacts.query.get((contact_id, uid))
		db.session.delete(contact_1)
		db.session.delete(contact_2)
		db.session.commit()
		return {
			'data': {},
			'errors': []
		}, 200


@app.route('/api/direct/<int:partner>', methods=['GET'])
def direct(partner):
	# partner - ID партнера, з яким веде переписку поточний користувач
	# отримати дані переписки (повідомлення) між поточним користувачем та partner'ом
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	args = request.args
	page = int(args.get('page', 1))
	count = int(args.get('count', 5))
	messages = Message.query.filter(
		( (Message.sender == partner) & (Message.receiver == uid) ) | ( (Message.sender == uid) & (Message.receiver == partner) )
	).order_by(Message.date.desc())
	messages_count = messages.count()
	if messages_count < count:
		messages_page = messages.all()
	else:
		start = (page - 1) * count
		messages_page = messages.limit(count).offset(start).all()

	items = []
	for m in messages_page:
		entry = {
			'id': m.id,
			'authorId': m.sender,
			'receiverId': m.receiver,
			'text': m.text
		}
		items.append(entry)

	return {
		'data': {'items': items, 'total': messages_count},
		'errors': []
	}, 200


@app.route('/api/message', methods=['POST'])
def message():
	# надіслати повідомлення
	uid = request.cookies.get('uid')
	if not uid:
		return {
			'data': {},
			'errors': ['Unauthorized']
		}, 401
	uid = int(uid)
	receiver = data.get('receiverId')
	text = data.get('text')

	new_message = Message(sender=uid, receiver=receiver, text=text)
	db.session.add(new_message)
	db.session.commit()
	db.session.refresh(new_message)
	return {
		'data': {
			'id': new_message.id
		},
		'errors': []
	}, 200



@app.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):
	# доступ до статичного файлу filename
	return send_from_directory('static/media', filename)


@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>')
def index(u_path):
	return render_template('index.html')


if __name__ == "__main__":
	app.run(debug=True)