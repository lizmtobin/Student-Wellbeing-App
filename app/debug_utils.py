from app import db
from app.models import User
import datetime


def reset_db():
    db.drop_all()
    db.create_all()
    seed_users()


def seed_users():
    users = [
        {"username": "amy", "email": "amy@b.com", "role": "Admin", "pw": "amy.pw"},
        {"username": "tom", "email": "tom@b.com", "pw": "amy.pw"},
        {"username": "yin", "email": "yin@b.com", "role": "Admin", "pw": "amy.pw"},
        {"username": "tariq", "email": "trq@b.com", "pw": "amy.pw"},
        {"username": "jo", "email": "jo@b.com", "pw": "amy.pw"},
    ]

    for u in users:
        pw = u.pop("pw")
        user = User(**u)
        user.set_password(pw)
        db.session.add(user)

    db.session.commit()
