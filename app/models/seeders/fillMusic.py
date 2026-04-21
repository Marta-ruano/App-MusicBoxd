from database import db
from models import Music, User


def fillMusic():
    music_list = [
        {
            "tipo": "Canción",
            "imagen": "/public/img/casar.jpg",
            "nombre": "No me quiero casar",
            "artista": "Bad Bunny",
            "genero": "Trap latino",
            "album": "Nadie sabe lo que va a pasar mañana",
            "num_canciones": None,
            "duracion": "3:45",
            "año": 2023,
            "url": "https://open.spotify.com/intl-es/track/39L3LdlHS3gqB62HPWaJRg",
        },
        {
            "tipo": "Canción",
            "imagen": "/public/img/manchild.jpg",
            "nombre": "Manchild",
            "artista": "Sabrina Carpenter",
            "genero": "Pop",
            "album": "Man's Best Friend",
            "num_canciones": None,
            "duracion": "3:12",
            "año": 2024,
            "url": "https://open.spotify.com/intl-es/album/4Py8hTvoKbdcFH3mQ2wXPo",
        },
        {
            "tipo": "Canción",
            "imagen": "/public/img/quevedo.jpg",
            "nombre": "NI BORRACHO",
            "artista": "Mora",
            "genero": "Reggaeton",
            "album": "Estrella",
            "num_canciones": None,
            "duracion": "3:05",
            "año": 2024,
            "url": "https://open.spotify.com/intl-es/track/3ltpc2goYCfKT8AbWwqQvc",
        },
        {
            "tipo": "Álbum",
            "imagen": "/public/img/lux.jpg",
            "nombre": "LUX",
            "artista": "Rosalia",
            "genero": "Pop",
            "album": None,
            "num_canciones": 12,
            "duracion": "49:35",
            "año": 2024,
            "url": "https://open.spotify.com/intl-es/album/3SUEJULSGgBDG1j4GQhfYY",
        },
        {
            "tipo": "Álbum",
            "imagen": "/public/img/dtmf.jpg",
            "nombre": "DeBÍ TiRAR MáS FOToS",
            "artista": "Bad Bunny",
            "genero": "Reggaeton",
            "album": None,
            "num_canciones": 15,
            "duracion": "1:02:00",
            "año": 2025,
            "url": "https://open.spotify.com/intl-es/track/3sK8wGT43QFpWrvNQsrQya",
        },
        {
            "tipo": "Álbum",
            "imagen": "/public/img/mora.jpg",
            "nombre": "LO MISMO DE SIEMPRE",
            "artista": "Mora",
            "genero": "Reggaeton",
            "album": None,
            "num_canciones": 10,
            "duracion": "59:21",
            "año": 2024,
            "url": "https://open.spotify.com/intl-es/album/3beZ5DRcWVTpXaU3ViLIF6",
        },
    ]

    owner_by_music = {
        "No me quiero casar": "nico",
        "Manchild": "laura",
        "NI BORRACHO": "clara",
        "LUX": "sofia",
        "DeBÍ TiRAR MáS FOToS": "andres",
        "LO MISMO DE SIEMPRE": "nico",
    }

    for m in music_list:
        owner_username = owner_by_music.get(m["nombre"])
        if not owner_username:
            raise Exception(f"No hay owner definido para: {m['nombre']}")

        owner = User.query.filter_by(username=owner_username).first()
        if not owner:
            raise Exception(f"No existe el usuario '{owner_username}'. Ejecuta fillUser() antes.")

        item = Music.query.filter_by(nombre=m["nombre"]).first()
        if item:
            item.tipo = m["tipo"]
            item.imagen = m["imagen"]
            item.nombre = m["nombre"]
            item.artista = m["artista"]
            item.genero = m["genero"]
            item.album = m["album"]
            item.num_canciones = m["num_canciones"]
            item.duracion = m["duracion"]
            item.año = m["año"]
            item.url = m["url"]
            item.user_id = owner.id
        else:
            item = Music(
                tipo=m["tipo"],
                imagen=m["imagen"],
                nombre=m["nombre"],
                artista=m["artista"],
                genero=m["genero"],
                album=m["album"],
                num_canciones=m["num_canciones"],
                duracion=m["duracion"],
                año=m["año"],
                url=m["url"],
                user_id=owner.id,
            )
            db.session.add(item)

    db.session.commit()
    print("Music data inserted/updated successfully.")