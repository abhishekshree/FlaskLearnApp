from flask import Flask, render_template, redirect, url_for, request, make_response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired , Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


app = Flask( __name__, static_folder='static' )

app.config.from_pyfile('config.py')

Bootstrap(app)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	subtitle = db.Column(db.String(200))
	author = db.Column(db.String(50))
	date_posted = db.Column(db.DateTime)
	content = db.Column(db.Text)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	email = db.Column(db.String(200))
	subject = db.Column(db.String(200))
	message = db.Column(db.Text)
	date = db.Column(db.DateTime)


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired(), Length(min=4 , max=15)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
	email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=100)])
	username = StringField('Username', validators=[InputRequired(), Length(min=4 , max=15)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])



@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('admin'))

		return render_template('error.html')

	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_pass = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
		db.session.add(new_user)
		db.session.commit()

		return "New user registered !"

	return render_template('signup.html', form=form)


@app.route('/')
def index():
	posts = Post.query.order_by(Post.date_posted.desc()).limit(5)

	return render_template('index.html', posts=posts)


@app.route('/all')
def all():
	po = Post.query.order_by(Post.date_posted.desc()).all()
	return render_template('all.html', p=po)


@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.filter_by(id=post_id).one()
	date_posted = post.date_posted.strftime('%B %d, %Y')

	return render_template('post.html', post=post, date_posted=date_posted)


@app.route('/add')
@login_required
def add():
	return render_template('add.html')


@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
	title = request.form['title']
	subtitle = request.form['subtitle']
	author = request.form['author']
	content = request.form['content']

	p = Post(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

	db.session.add(p)
	db.session.commit()

	return redirect(url_for('index'))


@app.route('/feedback')
def feed():
	feedbacks = Comment.query.all()
	return render_template('feedback.html', feedbacks=feedbacks)


@app.route('/addFeed', methods = ['GET', 'POST'])
def addFeed():
	name = request.form['name']
	email = request.form['email']
	sub = request.form['subject']
	message = request.form['message']

	d = Comment(name=name, email=email, subject=sub, message=message, date=datetime.now())
	db.session.add(d)

	db.session.commit()

	return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
	posts = Post.query.all()
	return render_template('admin.html', posts=posts)


@app.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
	r = Post.query.get_or_404(post_id)
	db.session.delete(r)
	db.session.commit()

	return redirect(url_for('admin'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/sitemap.xml")
def sitemap_xml():
    response= make_response(render_template("sitemap.xml"))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route("/robots.txt")
def robots_txt():
    return render_template("robots.txt")

if __name__ == "__main__":
	app.run()