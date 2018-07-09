import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

GOODREADS_KEY = "5PG7iFRIil3vkB38jRn9IA"


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

	return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():

	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		try:
			db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
			{"username": username, "password": password})
			db.commit()

			session["username"] = username
		except:
			return render_template("success.html", message="Something broke...")

		return render_template("success.html", message="your account has been created!", username=username)

@app.route("/login", methods=["POST"])
def login():

	if request.method == 'POST':		
		username = request.form.get('username')
		password = request.form.get('password')

		try:
			logged_in_user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
			session['username'] = logged_in_user['username']

		except: 
			return render_template("success.html", message="Something went wrong...")

		
		if logged_in_user is None:
			return render_template("success.html", message="that didn't work...")

		return redirect('search')

@app.route("/logout")
def logout():
	
	session.pop('username', None)

	return render_template("success.html", message="Successfully logged out!")

@app.route("/search", methods=["POST", "GET"])
def search():

	if request.method == 'POST':
		search = request.form.get('search')
		isbn_list = db.execute("SELECT * FROM books WHERE isbn = :isbn", 
								{"isbn": search}).fetchall()
		titles_list = db.execute("SELECT * FROM books WHERE title = :title", #PSCOPG2 error if LIKE used
								{"title":search}).fetchall()
		authors_list = db.execute("SELECT * FROM books WHERE author = :author",
								{"author":search}).fetchall()

		books_list = isbn_list + titles_list + authors_list

		if books_list == []:
			return render_template("success.html", message="No books found! Sorry!")

		return render_template("search.html", books_list=books_list)

	return render_template("search.html")

@app.route("/books/<int:id>", methods=["POST", "GET"])
def book(id):

	book = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()
	book_reviews = db.execute("SELECT * FROM reviews WHERE book = :book", {"book": book.id}).fetchall()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5PG7iFRIil3vkB38jRn9IA", "isbns": book.isbn})
	data = json.loads(res.content)
	item = data['books']
	y = item[0]
	
	try:
		average_rating = y['average_rating']
		work_ratings_count = y['work_ratings_count']
	except:
		average_rating = "Not available."
		work_ratings_count = "Not available."


	if request.method =='POST':
		body = request.form.get('body')
		rating = request.form.get('rating')

		for review in book_reviews:
			if session["username"] == review.author:
				return render_template("success.html", message="You have already left a review!")

		db.execute("INSERT INTO reviews (body, rating, author, book) VALUES (:body, :rating, :author, :book)",
					{"body": body, "rating": rating, "author": session["username"], "book": book.id})
		db.commit()

		return render_template("success.html", message="You have left a review fam!")


	if book is None:
		return render_template("success.html", message="No book here!")

	return render_template("book.html", book=book, book_reviews=book_reviews, average_rating=average_rating, work_ratings_count=work_ratings_count)

@app.route("/api/<isbn>")
def api(isbn):

	try:
		book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5PG7iFRIil3vkB38jRn9IA", "isbns": book.isbn})
		res = res.json()
	except:
		return abort(404)

	return jsonify(res)