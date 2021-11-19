from flask import Flask, flash, session, render_template, request, redirect
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


@app.route('/signup', methods=('GET', 'POST'))
def signup():
	if request.method == 'POST':
		email = request.form['email']
		login = request.form['login']
		password = request.form['password']
		password_repeat = request.form['password-repeat']
		valid = True

		if password != password_repeat:
			flash("Password doesn't match!")
			valid = False

		user_login = User.query.filter_by(login=login).first()
		user_email = User.query.filter_by(email=email).first()
		if user_login:
			flash('This login is already taken!')
			valid = False
		if user_email:
			flash('This email is already taken!')
			valid = False

		if valid:
			new_user = User(login=login, password=password, email=email)
			db.session.add(new_user)
			db.session.commit()
			session['uid'] = new_user.uid
			session['username'] = login
			return redirect('/')

		return render_template('signup.html')
	else:
		return render_template('signup.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		login = request.form['login']
		password = request.form['password']
		user = User.query.filter_by(login=login, password=password).first()
		if user:
			session['uid'] = user.uid
			session['username'] = login
			return redirect('/')
		else:
			flash('Invalid login or password!')
			return render_template('login.html')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/profile/<int:profid>')
def profile(profid):
	pass


@app.route('/blog/<int:blogid>/add-comment', methods=['GET', 'POST'])
@login_required
def add_comment(blogid):
	pass


@app.route('/comment/<int:comid>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comid):
	pass


@app.route('/comment/<int:comid>/delete')
@login_required
def delete_comment(comid):
	comment = Comment.query.get_or_404(comid)
	if session['uid'] != comment.user and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	blog = comment.blog
	entry_delete(comment)
	return redirect(f'/blog/{blog}')


if __name__ == "__main__":
	app.run(debug=True)