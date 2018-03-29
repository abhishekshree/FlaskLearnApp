from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask( __name__ )
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/abhishek/Videos/flaskWorks/Blog/blog.db'

db = SQLAlchemy(app)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	subtitle = db.Column(db.String(200))
	author = db.Column(db.String(50))
	date_posted = db.Column(db.DateTime)
	content = db.Column(db.Text)

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

if __name__ == '__main__':
	app.run(debug=True)