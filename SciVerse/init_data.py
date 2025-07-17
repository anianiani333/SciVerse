#init_data.py
from SciVerse.models import User
from SciVerse.ext import db, bcrypt
def create_main_user():
    if not User.query.filter_by(username='mainuser').first():
        hashed_pw = bcrypt.generate_password_hash('mainuserpass').decode('utf-8')
        admin = User(username='mainuser', email='mainuserann@book.com', password=hashed_pw, is_admin=True)
        db.session.add(admin)
        db.session.commit()
