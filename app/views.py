from flask import Flask, flash, session, request, render_template, make_response
from datetime import datetime
from functools import wraps
from models import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "???"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'...'


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session['uid'] is None:
			return redirect(url_for('login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/session', methods=('GET', 'POST', 'DELETE'))
def session():
	# SECURITY NOTE: додати підписні flask-сесії до кукі
	if request.method == 'GET':
		cookies = request.cookies
		if cookies.get('uid'):
			return {
			'status_code': 200,
			'status_message': 'Success.',
			'uid': cookies['uid'],
			'username': cookies['username']
			}
		else:
			return {'status_code': 404, 'status_message': 'User not found.'}

	elif request.method == 'POST':
		resp = make_response(render_template('index.html'))
		login = request.form['login']
		password = request.form['password']
		user = User.query.filter_by(login=login, password=password).first()
		if user:
			resp.set_cookie('uid', user.uid, max_age=None)
			resp.set_cookie('username', user.username, max_age=None)
			return {
			'status_code': 200,
			'status_message': 'Success.',
			'uid': user.uid,
			'username': user.username
			}
		else:
			return {'status_code': 204, 'status_message': 'Invalid login or password.'}

	elif request.method == 'DELETE':
		resp = make_response(render_template('index.html'))
		resp.set_cookie('uid', '', max_age=None)
		resp.set_cookie('username', '', max_age=None)
		return {'status_code': 200, 'status_message': 'Success.'}


@app.route('/user', defaults={'uid': None}, methods=['POST'])
@app.route('/user/<int:uid>', methods=['GET', 'DELETE'])
def user(uid):
	if request.method == 'GET':
		user = User.query.get(uid)
		if user:
			return {
			'status_code': 200,
			'status_message': 'Success.',
			'uid': user.uid,
			'username': user.username,
			# ...
			}
		else:
			return {'status_code': 404, 'status_message': 'User not found.'}
	elif request.method == 'POST':
		email = request.form['email']
		login = request.form['login']
		password = request.form['password']
		password_repeat = request.form['password-repeat']
		valid = True

		if password != password_repeat:
			return {'status_code': 401, 'status_message': "Passwords doesn't match."}

		user_login = User.query.filter_by(login=login).first()
		user_email = User.query.filter_by(email=email).first()
		if user_login:
			return {'status_code': 409, 'status_message': "Login already taken."}

		if user_email:
			return {'status_code': 409, 'status_message': "Email already taken."}

		new_user = User(login=login, password=password, email=email)
		db.session.add(new_user)
		db.session.commit()

		resp = make_response(render_template('index.html'))
		resp.set_cookie('uid', new_user.uid, max_age=None)
		resp.set_cookie('username', new_user.username, max_age=None)

		return {
			'status_code': 200,
			'status_message': 'Success.',
			'uid': new_user.uid,
			'username': new_user.username,
			# ...
			}

	elif request.method == 'DELETE':
		user = User.query.get(uid)
		db.session.delete(user)
		db.session.commit()

		resp.set_cookie('uid', '', max_age=None)
		resp.set_cookie('username', '', max_age=None)

		return {'status_code': 200, 'status_message': 'Success.'}


if __name__ == "__main__":
	app.run(debug=True)