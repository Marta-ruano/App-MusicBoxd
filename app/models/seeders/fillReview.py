from datetime import datetime
from database import db
from models import Review, User, Music


def stars_to_int(stars: str) -> int:
    return stars.count("★")


def fillReview():
    reviews_data = [
        {
            "username": "nico",
            "music_nombre": "No me quiero casar",
            "fecha": "2026-02-01",
            "valoracion": "★★★★★",
            "texto": "Increíble la motivación que trasmite esta canción, para centrarnos en nosotros mismos y no dejarnos llevar por personas que nos atrasan.",
        },
        {
            "username": "laura",
            "music_nombre": "Manchild",
            "fecha": "2026-02-03",
            "valoracion": "★★★★☆",
            "texto": "Me encanta cómo es capaz de explicar diferentes situaciones que se relacionan tan bien con las relaciones actuales",
        },
        {
            "username": "clara",
            "music_nombre": "NI BORRACHO",
            "fecha": "2026-02-24",
            "valoracion": "★★★★☆",
            "texto": "Tiene un ritmo que te hace escucharla sin parar y muy buena representación de las islas, no me mudo ni borracha",
        },
        {
            "username": "sofia",
            "music_nombre": "LUX",
            "fecha": "2026-02-06",
            "valoracion": "★★★★★",
            "texto": "Todo el álbum es una obra de arte al maximo nivel y me encanta como atraviesa idiomas, culturas y epocas",
        },
        {
            "username": "andres",
            "music_nombre": "DeBÍ TiRAR MáS FOToS",
            "fecha": "2026-02-07",
            "valoracion": "★★★★★",
            "texto": "Sinceramente a mi no me gusta mucho bad bunny, pero la verdad que con este disco la rompió",
        },
        {
            "username": "nico",
            "music_nombre": "LO MISMO DE SIEMPRE",
            "fecha": "2026-02-08",
            "valoracion": "★★★☆☆",
            "texto": "No es su mejor trabajo, pero tiene momentos brillantes y algunas canciones destacan muchísimo",
        },
    ]

    for r in reviews_data:
        user = User.query.filter_by(username=r["username"]).first()
        if not user:
            raise Exception("Ejecuta fillUser() antes que fillReview()")

        music = Music.query.filter_by(nombre=r["music_nombre"]).first()
        if not music:
            raise Exception("Ejecuta fillMusic() antes que fillReview()")

        fecha_date = datetime.strptime(r["fecha"], "%Y-%m-%d").date()
        val_int = stars_to_int(r["valoracion"])

        review = Review.query.filter_by(
            user_id=user.id,
            music_id=music.id,
            fecha=fecha_date
        ).first()

        if review:
            review.valoracion = val_int
            review.texto = r["texto"]
        else:
            review = Review(
                fecha=fecha_date,
                valoracion=val_int,
                texto=r["texto"],
                user_id=user.id,
                music_id=music.id,
            )
            db.session.add(review)

    db.session.commit()
    print("Review data inserted/updated successfully.")