from database import db
from models import User


def fillUser():
    users_data = [
        {"username": "marta", "email": "marta@gmail.com", "password": "1234", "role": "admin"},
        {"username": "nico", "email": "nico@gmail.com", "password": "1235", "role": "user"},
        {"username": "laura", "email": "laura@gmail.com", "password": "5678", "role": "user"},
        {"username": "clara", "email": "clara@gmail.com", "password": "9101", "role": "user"},
        {"username": "sofia", "email": "sofia@gmail.com", "password": "1213", "role": "user"},
        {"username": "andres", "email": "andres@gmail.com", "password": "1415", "role": "user"},
    ]

    for u in users_data:
        user = User.query.filter_by(email=u["email"]).first()

        if user:
            user.username = u["username"]
            user.role = u["role"]
            user.set_password(u["password"])
        else:
            user = User(username=u["username"], email=u["email"], role=u["role"])
            user.set_password(u["password"])
            db.session.add(user)

    db.session.commit()
    print("User data inserted successfully")