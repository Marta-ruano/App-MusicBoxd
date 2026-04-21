from database import db


class Music(db.Model):
    __tablename__ = "music"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tipo = db.Column(db.String(20), nullable=False)
    imagen = db.Column(db.String(255), nullable=True)

    nombre = db.Column(db.String(255), nullable=False)
    artista = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(255), nullable=True)

    num_canciones = db.Column(db.Integer, nullable=True)
    duracion = db.Column(db.String(20), nullable=True)
    año = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(500), nullable=True)

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="music_items")

    reviews = db.relationship("Review", backref="music", lazy=True, cascade="all, delete-orphan")