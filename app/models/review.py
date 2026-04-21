from database import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    fecha = db.Column(db.Date, nullable=False)
    valoracion = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    music_id = db.Column(db.Integer, db.ForeignKey("music.id"), nullable=False)
