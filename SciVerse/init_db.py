#SciVerse\init_db.py
from SciVerse.ext import db
from SciVerse.app import create_app
from SciVerse.models import User, Book, Comment, Cart, Order, OrderItem, Like

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized")


