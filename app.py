from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message ## not in use anymore 
from datetime import datetime

app = Flask( __name__ )
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/abhishek/Videos/flaskWorks/Blog/final.db'

db = SQLAlchemy(app)
# mail = Mail(app)

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


@app.route('/')
def index():
	posts = Post.query.order_by(Post.date_posted.desc()).all()
	
	return render_template('index.html', posts=posts)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.filter_by(id=post_id).one()
	date_posted = post.date_posted.strftime('%B %d, %Y')
	return render_template('post.html', post=post, date_posted=date_posted)

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/addpost', methods=['GET', 'POST'])
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


if __name__ == '__main__':
	app.run(debug=True)